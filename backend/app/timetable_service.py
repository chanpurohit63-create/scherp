from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlmodel import Session, select, func
from sqlalchemy import Integer, case

from . import models, schemas
from .database import engine
from .tenant import get_current_school_id
from .audit import log_audit


from .notification_service import NotificationService


DAYS_OF_WEEK = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def _get_school_id() -> Optional[int]:
    return get_current_school_id()


def _get_period_times(period_number: int, academic_year_id: int, school_id: Optional[int] = None) -> Optional[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.PeriodMaster).where(
            models.PeriodMaster.period_number == period_number,
            models.PeriodMaster.school_id == sid,
        )
        if academic_year_id:
            statement = statement.where(models.PeriodMaster.id == academic_year_id)
        period = session.exec(statement).first()
        if period:
            return {"start_time": period.start_time, "end_time": period.end_time, "period_name": period.period_name, "is_break": period.is_break}
    return None


def _resolve_period_times(day_of_week: int, period_number: int, academic_year_id: int, school_id: Optional[int] = None) -> dict:
    period = _get_period_times(period_number, academic_year_id, school_id)
    if period:
        return period
    base_hour = 8 + (period_number - 1)
    start_h = base_hour
    start_m = 0
    end_h = base_hour + 1
    end_m = 0
    return {
        "start_time": f"{start_h:02d}:{start_m:02d}",
        "end_time": f"{end_h:02d}:{end_m:02d}",
        "period_name": f"Period {period_number}",
        "is_break": False,
    }


def create_timetable_entry(timetable_in: schemas.TimetableCreate, current_user: models.User) -> models.Timetable:
    sid = _get_school_id()
    school_id = sid
    academic_year_id = timetable_in.academic_year_id

    with Session(engine) as session:
        ay = session.get(models.AcademicYear, academic_year_id)
        if ay and ay.school_id != school_id and school_id is not None:
            academic_year_id = ay.id

        existing = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == school_id,
                models.Timetable.academic_year_id == academic_year_id,
                models.Timetable.class_id == timetable_in.class_id,
                models.Timetable.day_of_week == timetable_in.day_of_week,
                models.Timetable.period == timetable_in.period,
                models.Timetable.section_id == timetable_in.section_id,
            )
        ).first()
        if existing:
            raise ValueError(f"Class already scheduled for this period on {DAYS_OF_WEEK[timetable_in.day_of_week]} period {timetable_in.period}")

        entry = models.Timetable(
            school_id=school_id,
            academic_year_id=academic_year_id,
            class_id=timetable_in.class_id,
            section_id=timetable_in.section_id,
            subject_id=timetable_in.subject_id,
            teacher_id=timetable_in.teacher_id,
            room_id=timetable_in.room_id,
            day_of_week=timetable_in.day_of_week,
            period=timetable_in.period,
            start_time=timetable_in.start_time,
            end_time=timetable_in.end_time,
            remarks=timetable_in.remarks,
            created_by=current_user.id,
        )

        conflicts = validate_timetable_conflicts(session, entry, school_id, exclude_id=None)
        if conflicts:
            for c in conflicts:
                log_conflict(session, school_id, academic_year_id, c, current_user.id)
            raise ValueError(f"Timetable conflicts detected: {len(conflicts)} conflict(s) found")

        session.add(entry)
        session.commit()
        session.refresh(entry)

        log_audit(
            user_id=current_user.id,
            school_id=school_id,
            action="create",
            resource="timetable",
            resource_id=entry.id,
            details=f"Created timetable entry for class {timetable_in.class_id} on {DAYS_OF_WEEK[timetable_in.day_of_week]} period {timetable_in.period}",
        )

        return entry


def get_timetable_entry(entry_id: int, school_id: Optional[int] = None) -> Optional[models.Timetable]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        entry = session.get(models.Timetable, entry_id)
        if not entry:
            return None
        if sid is not None and entry.school_id != sid:
            return None
        return entry


def list_timetable_entries(
    skip: int = 0,
    limit: int = 100,
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    section_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    room_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    day_of_week: Optional[int] = None,
    period: Optional[int] = None,
    school_id: Optional[int] = None,
) -> List[models.Timetable]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.Timetable)
        if sid is not None:
            statement = statement.where(models.Timetable.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.Timetable.academic_year_id == academic_year_id)
        if class_id is not None:
            statement = statement.where(models.Timetable.class_id == class_id)
        if section_id is not None:
            statement = statement.where(models.Timetable.section_id == section_id)
        if teacher_id is not None:
            statement = statement.where(models.Timetable.teacher_id == teacher_id)
        if room_id is not None:
            statement = statement.where(models.Timetable.room_id == room_id)
        if subject_id is not None:
            statement = statement.where(models.Timetable.subject_id == subject_id)
        if day_of_week is not None:
            statement = statement.where(models.Timetable.day_of_week == day_of_week)
        if period is not None:
            statement = statement.where(models.Timetable.period == period)
        statement = statement.order_by(models.Timetable.day_of_week, models.Timetable.period).offset(skip).limit(limit)
        return session.exec(statement).all()


def update_timetable_entry(entry_id: int, timetable_update: schemas.TimetableUpdate, current_user: models.User) -> Optional[models.Timetable]:
    sid = _get_school_id()
    with Session(engine) as session:
        entry = session.get(models.Timetable, entry_id)
        if not entry:
            return None
        if sid is not None and entry.school_id != sid:
            return None

        update_data = timetable_update.dict(exclude_unset=True)
        old_values = {k: getattr(entry, k) for k in update_data.keys()}

        for k, v in update_data.items():
            setattr(entry, k, v)

        conflicts = validate_timetable_conflicts(session, entry, sid, exclude_id=entry_id)
        if conflicts:
            for c in conflicts:
                log_conflict(session, sid, entry.academic_year_id, c, current_user.id)
            raise ValueError(f"Timetable conflicts detected: {len(conflicts)} conflict(s) found")

        entry.updated_by = current_user.id
        session.add(entry)
        session.commit()
        session.refresh(entry)

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="update",
            resource="timetable",
            resource_id=entry_id,
            before_values=str(old_values),
            after_values=str(update_data),
            details=f"Updated timetable entry {entry_id}",
        )

        return entry


def delete_timetable_entry(entry_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        entry = session.get(models.Timetable, entry_id)
        if not entry:
            return False
        if sid is not None and entry.school_id != sid:
            return False

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="delete",
            resource="timetable",
            resource_id=entry_id,
            details=f"Deleted timetable entry for class {entry.class_id} on {DAYS_OF_WEEK[entry.day_of_week]} period {entry.period}",
        )

        session.delete(entry)
        session.commit()
        return True


def duplicate_timetable(source_academic_year_id: int, target_academic_year_id: int, current_user: models.User) -> int:
    sid = _get_school_id()
    with Session(engine) as session:
        source_entries = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.academic_year_id == source_academic_year_id,
            )
        ).all()

        count = 0
        for entry in source_entries:
            new_entry = models.Timetable(
                school_id=sid,
                academic_year_id=target_academic_year_id,
                class_id=entry.class_id,
                section_id=entry.section_id,
                subject_id=entry.subject_id,
                teacher_id=entry.teacher_id,
                room_id=entry.room_id,
                day_of_week=entry.day_of_week,
                period=entry.period,
                start_time=entry.start_time,
                end_time=entry.end_time,
                status="active",
                remarks=entry.remarks,
                created_by=current_user.id,
            )
            session.add(new_entry)
            count += 1

        session.commit()

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="duplicate",
            resource="timetable",
            details=f"Duplicated timetable from academic year {source_academic_year_id} to {target_academic_year_id} ({count} entries)",
        )

        return count


def copy_timetable_between_sections(
    source_academic_year_id: int,
    source_section_id: int,
    target_section_id: int,
    target_class_id: int,
    target_academic_year_id: int,
    current_user: models.User,
) -> int:
    sid = _get_school_id()
    with Session(engine) as session:
        source_entries = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.academic_year_id == source_academic_year_id,
                models.Timetable.section_id == source_section_id,
            )
        ).all()

        count = 0
        for entry in source_entries:
            new_entry = models.Timetable(
                school_id=sid,
                academic_year_id=target_academic_year_id,
                class_id=target_class_id,
                section_id=target_section_id,
                subject_id=entry.subject_id,
                teacher_id=entry.teacher_id,
                room_id=entry.room_id,
                day_of_week=entry.day_of_week,
                period=entry.period,
                start_time=entry.start_time,
                end_time=entry.end_time,
                status="active",
                remarks=entry.remarks,
                created_by=current_user.id,
            )
            conflicts = validate_timetable_conflicts(session, new_entry, sid, exclude_id=None)
            if not conflicts:
                session.add(new_entry)
                count += 1

        session.commit()

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="copy",
            resource="timetable",
            details=f"Copied timetable from section {source_section_id} to section {target_section_id} ({count} entries)",
        )

        return count


def bulk_generate_timetable(config: schemas.TimetableGenerateRequest, current_user: models.User) -> Dict[str, Any]:
    sid = _get_school_id()
    with Session(engine) as session:
        ay = session.get(models.AcademicYear, config.academic_year_id)
        if not ay:
            raise ValueError("Academic year not found")

        classes = session.exec(
            select(models.SchoolClass).where(models.SchoolClass.school_id == sid)
        ).all()

        sections = session.exec(
            select(models.Section).where(models.Section.school_id == sid)
        ).all()

        rooms = session.exec(
            select(models.Room).where(models.Room.school_id == sid, models.Room.is_active == True)
        ).all()

        allocations = session.exec(
            select(models.SubjectAllocation).where(
                models.SubjectAllocation.school_id == sid,
                models.SubjectAllocation.class_id.in_([c.id for c in classes]),
            )
        ).all()

        generated_count = 0
        conflicts_found = 0

        for class_obj in classes:
            for section in sections:
                if section.class_id != class_obj.id:
                    continue
                for alloc in allocations:
                    if alloc.class_id != class_obj.id:
                        continue
                    if alloc.section_id is not None and alloc.section_id != section.id:
                        continue

                    subject = session.get(models.Subject, alloc.subject_id)
                    if not subject:
                        continue

                    teacher = session.get(models.Teacher, alloc.teacher_id)
                    if not teacher:
                        continue

                    available_rooms = [r for r in rooms if r.room_type in ("Classroom", "Lab", "Computer Lab")]
                    if not available_rooms:
                        available_rooms = rooms

                    for day in config.working_days:
                        for period_num in range(1, config.periods_per_day + 1):
                            period_info = _resolve_period_times(day, period_num, config.academic_year_id, sid)
                            if period_info.get("is_break") and period_num in config.break_periods:
                                continue

                            room = available_rooms[period_num % len(available_rooms)] if available_rooms else None

                            entry = models.Timetable(
                                school_id=sid,
                                academic_year_id=config.academic_year_id,
                                class_id=class_obj.id,
                                section_id=section.id,
                                subject_id=alloc.subject_id,
                                teacher_id=alloc.teacher_id,
                                room_id=room.id if room else None,
                                day_of_week=day,
                                period=period_num,
                                start_time=period_info["start_time"],
                                end_time=period_info["end_time"],
                                status="active",
                            )

                            conflicts = validate_timetable_conflicts(session, entry, sid, exclude_id=None)
                            if conflicts:
                                conflicts_found += len(conflicts)
                                for c in conflicts:
                                    log_conflict(session, sid, config.academic_year_id, c, current_user.id)
                            else:
                                session.add(entry)
                                generated_count += 1

        session.commit()

        log_entry = models.TimetableGeneratorLog(
            school_id=sid,
            academic_year_id=config.academic_year_id,
            generated_by=current_user.id,
            generation_type="auto",
            config=str(config.dict()),
            result_summary=str({"generated": generated_count, "conflicts": conflicts_found}),
            conflicts_found=conflicts_found,
            conflicts_resolved=0,
            status="completed" if conflicts_found == 0 else "partial",
        )
        session.add(log_entry)
        session.commit()

        return {
            "generated": generated_count,
            "conflicts_found": conflicts_found,
            "log_id": log_entry.id,
        }


def validate_timetable_conflicts(
    session: Session,
    entry: models.Timetable,
    school_id: Optional[int],
    exclude_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    conflicts = []

    teacher_conflicts = session.exec(
        select(models.Timetable).where(
            models.Timetable.school_id == school_id,
            models.Timetable.teacher_id == entry.teacher_id,
            models.Timetable.day_of_week == entry.day_of_week,
            models.Timetable.period == entry.period,
            models.Timetable.id != exclude_id,
        )
    ).all()
    for tc in teacher_conflicts:
        conflicts.append({
            "type": "teacher",
            "description": f"Teacher already assigned to {DAYS_OF_WEEK[tc.day_of_week]} period {tc.period}",
            "conflicting_record_id": tc.id,
        })

    room_conflicts = session.exec(
        select(models.Timetable).where(
            models.Timetable.school_id == school_id,
            models.Timetable.room_id == entry.room_id,
            models.Timetable.day_of_week == entry.day_of_week,
            models.Timetable.period == entry.period,
            models.Timetable.id != exclude_id,
        )
    ).all()
    for rc in room_conflicts:
        conflicts.append({
            "type": "room",
            "description": f"Room already occupied on {DAYS_OF_WEEK[rc.day_of_week]} period {rc.period}",
            "conflicting_record_id": rc.id,
        })

    class_conflicts = session.exec(
        select(models.Timetable).where(
            models.Timetable.school_id == school_id,
            models.Timetable.class_id == entry.class_id,
            models.Timetable.day_of_week == entry.day_of_week,
            models.Timetable.period == entry.period,
            models.Timetable.id != exclude_id,
        )
    ).all()
    for cc in class_conflicts:
        conflicts.append({
            "type": "class",
            "description": f"Class already scheduled on {DAYS_OF_WEEK[cc.day_of_week]} period {cc.period}",
            "conflicting_record_id": cc.id,
        })

    if entry.section_id is not None:
        section_conflicts = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == school_id,
                models.Timetable.section_id == entry.section_id,
                models.Timetable.day_of_week == entry.day_of_week,
                models.Timetable.period == entry.period,
                models.Timetable.id != exclude_id,
            )
        ).all()
        for sc in section_conflicts:
            conflicts.append({
                "type": "section",
                "description": f"Section conflict on {DAYS_OF_WEEK[sc.day_of_week]} period {sc.period}",
                "conflicting_record_id": sc.id,
            })

    subject_conflicts = session.exec(
        select(models.Timetable).where(
            models.Timetable.school_id == school_id,
            models.Timetable.class_id == entry.class_id,
            models.Timetable.section_id == entry.section_id,
            models.Timetable.subject_id == entry.subject_id,
            models.Timetable.day_of_week == entry.day_of_week,
            models.Timetable.period == entry.period,
            models.Timetable.id != exclude_id,
        )
    ).all()
    for subc in subject_conflicts:
        conflicts.append({
            "type": "subject",
            "description": f"Duplicate subject entry for {DAYS_OF_WEEK[subc.day_of_week]} period {subc.period}",
            "conflicting_record_id": subc.id,
        })

    return conflicts


def log_conflict(session: Session, school_id: int, academic_year_id: int, conflict: Dict[str, Any], user_id: Optional[int]):
    log = models.TimetableConflictLog(
        school_id=school_id,
        academic_year_id=academic_year_id,
        conflict_type=conflict.get("type", "unknown"),
        conflict_description=conflict.get("description", ""),
        day_of_week=conflict.get("day_of_week", 0),
        period_number=conflict.get("period_number", 0),
        teacher_id=conflict.get("teacher_id"),
        class_id=conflict.get("class_id"),
        section_id=conflict.get("section_id"),
        room_id=conflict.get("room_id"),
        subject_id=conflict.get("subject_id"),
        conflicting_record_id=conflict.get("conflicting_record_id"),
        resolved=False,
    )
    session.add(log)


def get_conflicts(
    academic_year_id: Optional[int] = None,
    school_id: Optional[int] = None,
    resolved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.TimetableConflictLog]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.TimetableConflictLog).where(models.TimetableConflictLog.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.TimetableConflictLog.academic_year_id == academic_year_id)
        if resolved is not None:
            statement = statement.where(models.TimetableConflictLog.resolved == resolved)
        statement = statement.order_by(models.TimetableConflictLog.created_on.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()


def resolve_conflict(conflict_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        conflict = session.get(models.TimetableConflictLog, conflict_id)
        if not conflict:
            return False
        if sid is not None and conflict.school_id != sid:
            return False
        conflict.resolved = True
        conflict.resolved_by = current_user.id
        conflict.resolved_at = datetime.utcnow()
        session.add(conflict)
        session.commit()
        return True


def get_teacher_timetable(teacher_id: int, academic_year_id: Optional[int] = None, school_id: Optional[int] = None) -> List[models.Timetable]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.Timetable).where(models.Timetable.teacher_id == teacher_id, models.Timetable.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.Timetable.academic_year_id == academic_year_id)
        statement = statement.order_by(models.Timetable.day_of_week, models.Timetable.period)
        return session.exec(statement).all()


def get_class_timetable(class_id: int, academic_year_id: Optional[int] = None, school_id: Optional[int] = None) -> List[models.Timetable]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.Timetable).where(models.Timetable.class_id == class_id, models.Timetable.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.Timetable.academic_year_id == academic_year_id)
        statement = statement.order_by(models.Timetable.day_of_week, models.Timetable.period)
        return session.exec(statement).all()


def get_room_timetable(room_id: int, academic_year_id: Optional[int] = None, school_id: Optional[int] = None) -> List[models.Timetable]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.Timetable).where(models.Timetable.room_id == room_id, models.Timetable.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.Timetable.academic_year_id == academic_year_id)
        statement = statement.order_by(models.Timetable.day_of_week, models.Timetable.period)
        return session.exec(statement).all()


def get_student_timetable(student_id: int, academic_year_id: Optional[int] = None, school_id: Optional[int] = None) -> List[models.Timetable]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        student = session.get(models.Student, student_id)
        if not student or (sid is not None and student.school_id != sid):
            return []

        enrollments = session.exec(
            select(models.Enrollment).where(
                models.Enrollment.student_id == student_id,
                models.Enrollment.school_id == sid,
            )
        ).all()

        if not enrollments:
            return []

        class_ids = [e.class_id for e in enrollments]
        section_ids = [e.section_id for e in enrollments if e.section_id]

        statement = select(models.Timetable).where(
            models.Timetable.school_id == sid,
            models.Timetable.class_id.in_(class_ids),
        )
        if section_ids:
            statement = statement.where(models.Timetable.section_id.in_(section_ids))
        if academic_year_id is not None:
            statement = statement.where(models.Timetable.academic_year_id == academic_year_id)
        statement = statement.order_by(models.Timetable.day_of_week, models.Timetable.period)
        return session.exec(statement).all()


def get_teacher_availability(teacher_id: int, school_id: Optional[int] = None) -> List[models.TeacherAvailability]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.TeacherAvailability).where(models.TeacherAvailability.teacher_id == teacher_id, models.TeacherAvailability.school_id == sid)
        ).all()


def set_teacher_availability(teacher_id: int, availability_in: List[schemas.TeacherAvailabilityCreate], current_user: models.User) -> List[models.TeacherAvailability]:
    sid = _get_school_id()
    with Session(engine) as session:
        existing = session.exec(
            select(models.TeacherAvailability).where(models.TeacherAvailability.teacher_id == teacher_id, models.TeacherAvailability.school_id == sid)
        ).all()
        for e in existing:
            session.delete(e)

        new_availability = []
        for a in availability_in:
            av = models.TeacherAvailability(
                teacher_id=teacher_id,
                school_id=sid,
                day_of_week=a.day_of_week,
                period_number=a.period_number,
                is_available=a.is_available,
                availability_type=a.availability_type,
            )
            session.add(av)
            new_availability.append(av)

        session.commit()
        for av in new_availability:
            session.refresh(av)

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="update",
            resource="teacher_availability",
            resource_id=teacher_id,
            details=f"Updated availability for teacher {teacher_id}",
        )

        return new_availability


def get_timetable_dashboard(school_id: Optional[int] = None) -> Dict[str, Any]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        today = date.today().weekday()

        total_classes = session.exec(select(func.count(models.Timetable.id)).where(models.Timetable.school_id == sid)).one() or 0
        total_teachers = session.exec(select(func.count(models.Teacher.id)).where(models.Teacher.school_id == sid)).one() or 0
        today_classes = session.exec(
            select(func.count(models.Timetable.id)).where(
                models.Timetable.school_id == sid,
                models.Timetable.day_of_week == today,
                models.Timetable.status == "active",
            )
        ).one() or 0

        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        running_classes = session.exec(
            select(func.count(models.Timetable.id)).where(
                models.Timetable.school_id == sid,
                models.Timetable.day_of_week == today,
                models.Timetable.status == "active",
                models.Timetable.start_time <= current_time,
                models.Timetable.end_time >= current_time,
            )
        ).one() or 0

        total_rooms = session.exec(select(func.count(models.Room.id)).where(models.Room.school_id == sid)).one() or 0
        occupied_rooms = session.exec(
            select(func.count(func.distinct(models.Timetable.room_id))).where(
                models.Timetable.school_id == sid,
                models.Timetable.day_of_week == today,
                models.Timetable.status == "active",
                models.Timetable.start_time <= current_time,
                models.Timetable.end_time >= current_time,
                models.Timetable.room_id.is_not(None),
            )
        ).one() or 0
        free_rooms = total_rooms - occupied_rooms

        duration = (
            func.cast(func.substring(models.Timetable.end_time, 1, 2), Integer) * 60
            + func.cast(func.substring(models.Timetable.end_time, 4, 2), Integer)
            - func.cast(func.substring(models.Timetable.start_time, 1, 2), Integer) * 60
            - func.cast(func.substring(models.Timetable.start_time, 4, 2), Integer)
        )
        total_teaching_hours = session.exec(
            select(
                func.sum(
                    case(
                        (duration > 0, duration),
                        else_=0,
                    )
                )
            ).where(models.Timetable.school_id == sid)
        ).one() or 0

        avg_teaching_hours = round(total_teaching_hours / total_teachers, 2) if total_teachers > 0 else 0.0
        teacher_utilization = round((total_teaching_hours / (total_teachers * 40)) * 100, 1) if total_teachers > 0 else 0.0
        room_utilization = round((occupied_rooms / total_rooms) * 100, 1) if total_rooms > 0 else 0.0

        upcoming = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.status == "active",
            ).order_by(models.Timetable.day_of_week, models.Timetable.period).limit(10)
        ).all()

        return {
            "total_classes": total_classes,
            "total_teachers": total_teachers,
            "today_classes": today_classes,
            "running_classes": running_classes,
            "free_rooms": free_rooms,
            "occupied_rooms": occupied_rooms,
            "teacher_utilization": teacher_utilization,
            "room_utilization": room_utilization,
            "avg_teaching_hours": avg_teaching_hours,
            "upcoming_classes": [
                {
                    "id": t.id,
                    "class_id": t.class_id,
                    "subject_id": t.subject_id,
                    "teacher_id": t.teacher_id,
                    "room_id": t.room_id,
                    "day_of_week": t.day_of_week,
                    "period": t.period,
                    "start_time": t.start_time,
                    "end_time": t.end_time,
                }
                for t in upcoming
            ],
        }


def get_period_master(school_id: Optional[int] = None) -> List[models.PeriodMaster]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.PeriodMaster).where(models.PeriodMaster.school_id == sid).order_by(models.PeriodMaster.sort_order)
        ).all()


def create_period_master(period_in: schemas.PeriodMasterCreate, current_user: models.User) -> models.PeriodMaster:
    sid = current_user.school_id
    period = models.PeriodMaster(
        school_id=sid,
        period_name=period_in.period_name,
        period_number=period_in.period_number,
        start_time=period_in.start_time,
        end_time=period_in.end_time,
        is_break=period_in.is_break,
        is_assembly=period_in.is_assembly,
        is_sports=period_in.is_sports,
        is_library=period_in.is_library,
        is_practical=period_in.is_practical,
        sort_order=period_in.sort_order,
    )
    with Session(engine) as session:
        session.add(period)
        session.commit()
        session.refresh(period)
    return period


def update_period_master(period_id: int, period_update: schemas.PeriodMasterUpdate, current_user: models.User) -> Optional[models.PeriodMaster]:
    sid = _get_school_id()
    with Session(engine) as session:
        period = session.get(models.PeriodMaster, period_id)
        if not period or (sid is not None and period.school_id != sid):
            return None
        update_data = period_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(period, k, v)
        session.add(period)
        session.commit()
        session.refresh(period)
        return period


def delete_period_master(period_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        period = session.get(models.PeriodMaster, period_id)
        if not period or (sid is not None and period.school_id != sid):
            return False
        session.delete(period)
        session.commit()
        return True


def get_room_allocation(school_id: Optional[int] = None) -> List[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        rooms = session.exec(select(models.Room).where(models.Room.school_id == sid)).all()
        today = date.today().weekday()
        current_time = datetime.utcnow().strftime("%H:%M")
        result = []
        for room in rooms:
            current_class = session.exec(
                select(models.Timetable).where(
                    models.Timetable.room_id == room.id,
                    models.Timetable.school_id == sid,
                    models.Timetable.day_of_week == today,
                    models.Timetable.status == "active",
                    models.Timetable.start_time <= current_time,
                    models.Timetable.end_time >= current_time,
                )
            ).first()
            daily_usage = session.exec(
                select(func.count(models.Timetable.id)).where(
                    models.Timetable.room_id == room.id,
                    models.Timetable.school_id == sid,
                    models.Timetable.day_of_week == today,
                )
            ).one() or 0
            weekly_usage = session.exec(
                select(func.count(models.Timetable.id)).where(
                    models.Timetable.room_id == room.id,
                    models.Timetable.school_id == sid,
                )
            ).one() or 0
            result.append({
                "room": room,
                "current_class": current_class,
                "daily_usage": daily_usage,
                "weekly_usage": weekly_usage,
                "is_available": current_class is None,
            })
        return result


# ========== BULK OPERATIONS ==========

def bulk_import_timetable(entries_in: List[schemas.TimetableCreate], current_user: models.User) -> Dict[str, Any]:
    sid = _get_school_id()
    created = 0
    skipped = 0
    errors = []

    with Session(engine) as session:
        for i, entry_in in enumerate(entries_in):
            try:
                existing = session.exec(
                    select(models.Timetable).where(
                        models.Timetable.school_id == sid,
                        models.Timetable.academic_year_id == entry_in.academic_year_id,
                        models.Timetable.class_id == entry_in.class_id,
                        models.Timetable.day_of_week == entry_in.day_of_week,
                        models.Timetable.period == entry_in.period,
                        models.Timetable.section_id == entry_in.section_id,
                    )
                ).first()
                if existing:
                    skipped += 1
                    continue

                entry = models.Timetable(
                    school_id=sid,
                    academic_year_id=entry_in.academic_year_id,
                    class_id=entry_in.class_id,
                    section_id=entry_in.section_id,
                    subject_id=entry_in.subject_id,
                    teacher_id=entry_in.teacher_id,
                    room_id=entry_in.room_id,
                    day_of_week=entry_in.day_of_week,
                    period=entry_in.period,
                    start_time=entry_in.start_time,
                    end_time=entry_in.end_time,
                    status="draft",
                    remarks=entry_in.remarks,
                    created_by=current_user.id,
                )
                conflicts = validate_timetable_conflicts(session, entry, sid, exclude_id=None)
                if conflicts:
                    errors.append({"row": i + 1, "message": f"Conflict: {conflicts[0]['description']}"})
                    skipped += 1
                    continue

                session.add(entry)
                created += 1
            except Exception as e:
                errors.append({"row": i + 1, "message": str(e)})

        session.commit()

    log_audit(
        user_id=current_user.id,
        school_id=sid,
        action="bulk_import",
        resource="timetable",
        details=f"Bulk imported {created} timetable entries, {skipped} skipped, {len(errors)} errors",
    )

    return {"created": created, "skipped": skipped, "errors": errors}


def bulk_update_timetable(entry_ids: List[int], updates: dict, current_user: models.User) -> Dict[str, Any]:
    sid = _get_school_id()
    updated = 0
    failed = 0

    with Session(engine) as session:
        for entry_id in entry_ids:
            entry = session.get(models.Timetable, entry_id)
            if not entry or (sid is not None and entry.school_id != sid):
                failed += 1
                continue

            old_values = {k: getattr(entry, k) for k in updates.keys() if hasattr(entry, k)}
            for k, v in updates.items():
                if hasattr(entry, k):
                    setattr(entry, k, v)

            conflicts = validate_timetable_conflicts(session, entry, sid, exclude_id=entry_id)
            if conflicts:
                failed += 1
                for c in conflicts:
                    log_conflict(session, sid, entry.academic_year_id, c, current_user.id)
                continue

            entry.updated_by = current_user.id
            session.add(entry)
            updated += 1

        session.commit()

    log_audit(
        user_id=current_user.id,
        school_id=sid,
        action="bulk_update",
        resource="timetable",
        details=f"Bulk updated {updated} timetable entries, {failed} failed",
    )

    return {"updated": updated, "failed": failed}


def bulk_delete_timetable(entry_ids: List[int], current_user: models.User) -> Dict[str, Any]:
    sid = _get_school_id()
    deleted = 0
    failed = 0

    with Session(engine) as session:
        for entry_id in entry_ids:
            entry = session.get(models.Timetable, entry_id)
            if not entry or (sid is not None and entry.school_id != sid):
                failed += 1
                continue
            session.delete(entry)
            deleted += 1

        session.commit()

    log_audit(
        user_id=current_user.id,
        school_id=sid,
        action="bulk_delete",
        resource="timetable",
        details=f"Bulk deleted {deleted} timetable entries, {failed} failed",
    )

    return {"deleted": deleted, "failed": failed}


# ========== PUBLISH / DRAFT ==========

def publish_timetable(academic_year_id: int, current_user: models.User) -> int:
    sid = _get_school_id()
    with Session(engine) as session:
        entries = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.academic_year_id == academic_year_id,
                models.Timetable.status == "draft",
            )
        ).all()

        count = 0
        for entry in entries:
            entry.status = "active"
            entry.updated_by = current_user.id
            session.add(entry)
            count += 1

        session.commit()

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="publish",
            resource="timetable",
            details=f"Published timetable for academic year {academic_year_id} ({count} entries)",
        )

        return count


def unpublish_timetable(academic_year_id: int, current_user: models.User) -> int:
    sid = _get_school_id()
    with Session(engine) as session:
        entries = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.academic_year_id == academic_year_id,
                models.Timetable.status == "active",
            )
        ).all()

        count = 0
        for entry in entries:
            entry.status = "draft"
            entry.updated_by = current_user.id
            session.add(entry)
            count += 1

        session.commit()

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="unpublish",
            resource="timetable",
            details=f"Unpublished timetable for academic year {academic_year_id} ({count} entries)",
        )

        return count


# ========== REGENERATE ==========

def regenerate_timetable(academic_year_id: int, current_user: models.User) -> Dict[str, Any]:
    sid = _get_school_id()
    with Session(engine) as session:
        existing = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.academic_year_id == academic_year_id,
            )
        ).all()

        deleted = len(existing)
        for entry in existing:
            session.delete(entry)

        session.commit()

        config = schemas.TimetableGenerateRequest(
            academic_year_id=academic_year_id,
            working_days=[0, 1, 2, 3, 4, 5],
            periods_per_day=6,
            auto_assign_teachers=True,
            auto_assign_rooms=True,
            auto_assign_periods=True,
        )
        result = bulk_generate_timetable(config, current_user)
        result["deleted_existing"] = deleted

        return result


# ========== TIMETABLE REPORTS ==========

def get_teacher_workload_report(school_id: Optional[int] = None) -> List[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        teachers = session.exec(
            select(models.Teacher).where(models.Teacher.school_id == sid)
        ).all()

        result = []
        for teacher in teachers:
            entries = session.exec(
                select(models.Timetable).where(
                    models.Timetable.school_id == sid,
                    models.Timetable.teacher_id == teacher.id,
                    models.Timetable.status == "active",
                )
            ).all()

            total_periods = len(entries)
            days_with_classes = len(set(e.day_of_week for e in entries))
            subjects = list(set(e.subject_id for e in entries))
            classes = list(set(e.class_id for e in entries))
            total_hours = sum(
                (int(e.end_time.split(":")[0]) - int(e.start_time.split(":")[0]))
                if e.start_time and e.end_time else 1
                for e in entries
            )

            result.append({
                "teacher_id": teacher.id,
                "teacher_name": teacher.employee_no or f"Teacher #{teacher.id}",
                "total_periods": total_periods,
                "days_with_classes": days_with_classes,
                "subjects_count": len(subjects),
                "classes_count": len(classes),
                "total_hours": total_hours,
                "avg_hours_per_day": round(total_hours / max(days_with_classes, 1), 1),
            })

        return result


def get_room_occupancy_report(school_id: Optional[int] = None) -> List[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        rooms = session.exec(
            select(models.Room).where(models.Room.school_id == sid)
        ).all()

        result = []
        for room in rooms:
            total_slots = session.exec(
                select(func.count(models.Timetable.id)).where(
                    models.Timetable.room_id == room.id,
                    models.Timetable.school_id == sid,
                )
            ).one() or 0

            active_slots = session.exec(
                select(func.count(models.Timetable.id)).where(
                    models.Timetable.room_id == room.id,
                    models.Timetable.school_id == sid,
                    models.Timetable.status == "active",
                )
            ).one() or 0

            utilization = round((active_slots / max(total_slots, 1)) * 100, 1)

            result.append({
                "room_id": room.id,
                "room_name": room.room_name,
                "room_number": room.room_number,
                "room_type": room.room_type,
                "capacity": room.capacity,
                "total_slots": total_slots,
                "active_slots": active_slots,
                "utilization_percent": utilization,
            })

        return result


def get_class_timetable_report(class_id: int, school_id: Optional[int] = None) -> List[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        entries = session.exec(
            select(models.Timetable).where(
                models.Timetable.school_id == sid,
                models.Timetable.class_id == class_id,
                models.Timetable.status == "active",
            )
        ).all()

        result = []
        for entry in entries:
            result.append({
                "day": DAYS_OF_WEEK.get(entry.day_of_week, str(entry.day_of_week)),
                "period": entry.period,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "subject_id": entry.subject_id,
                "teacher_id": entry.teacher_id,
                "room_id": entry.room_id,
                "section_id": entry.section_id,
            })

        return result


def get_subject_distribution_report(school_id: Optional[int] = None) -> List[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        subjects = session.exec(
            select(models.Subject).where(models.Subject.school_id == sid)
        ).all()

        result = []
        for subject in subjects:
            entries = session.exec(
                select(models.Timetable).where(
                    models.Timetable.school_id == sid,
                    models.Timetable.subject_id == subject.id,
                    models.Timetable.status == "active",
                )
            ).all()

            teachers = list(set(e.teacher_id for e in entries))
            classes = list(set(e.class_id for e in entries))

            result.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "subject_code": subject.code,
                "total_periods": len(entries),
                "teachers_count": len(teachers),
                "classes_count": len(classes),
            })

        return result


def get_period_analysis_report(school_id: Optional[int] = None) -> List[dict]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        periods = session.exec(
            select(models.PeriodMaster).where(models.PeriodMaster.school_id == sid)
        ).all()

        result = []
        for period in periods:
            entries = session.exec(
                select(models.Timetable).where(
                    models.Timetable.school_id == sid,
                    models.Timetable.period == period.period_number,
                )
            ).all()

            result.append({
                "period_id": period.id,
                "period_name": period.period_name,
                "period_number": period.period_number,
                "start_time": period.start_time,
                "end_time": period.end_time,
                "is_break": period.is_break,
                "total_classes": len(entries),
            })

        return result


# ========== TIMETABLE NOTIFICATIONS ==========

async def notify_timetable_published(academic_year_id: int, class_ids: List[int], school_id: Optional[int] = None):
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        ay = session.get(models.AcademicYear, academic_year_id)
        ay_name = ay.name if ay else f"Year {academic_year_id}"

        for cid in class_ids:
            students = session.exec(
                select(models.Enrollment).where(
                    models.Enrollment.class_id == cid,
                    models.Enrollment.school_id == sid,
                )
            ).all()

            for enrollment in students:
                student = session.get(models.Student, enrollment.student_id)
                if student:
                    await NotificationService.create_and_send(
                        user_id=student.user_id,
                        title="Timetable Published",
                        message=f"The timetable for {ay_name} has been published for your class.",
                        category="Timetable",
                        priority="normal",
                        related_module="timetable",
                        related_record_id=academic_year_id,
                    )

            teachers_in_class = session.exec(
                select(models.SubjectAllocation).where(
                    models.SubjectAllocation.class_id == cid,
                    models.SubjectAllocation.school_id == sid,
                )
            ).all()

            for alloc in teachers_in_class:
                teacher = session.get(models.Teacher, alloc.teacher_id)
                if teacher:
                    await NotificationService.create_and_send(
                        user_id=teacher.user_id,
                        title="Timetable Published",
                        message=f"The timetable for {ay_name} has been published. Check your schedule.",
                        category="Timetable",
                        priority="normal",
                        related_module="timetable",
                        related_record_id=academic_year_id,
                    )


async def notify_timetable_changed(entry_id: int, change_type: str, school_id: Optional[int] = None):
    school_id_val = school_id or _get_school_id()
    with Session(engine) as session:
        entry = session.get(models.Timetable, entry_id)
        if not entry:
            return

        teacher = session.get(models.Teacher, entry.teacher_id)
        if teacher:
            await NotificationService.create_and_send(
                user_id=teacher.user_id,
                title="Timetable Updated",
                message=f"Your timetable has been {change_type}. Please review your schedule.",
                category="Timetable",
                priority="high",
                related_module="timetable",
                related_record_id=entry_id,
            )


async def notify_room_changed(room_id: int, school_id: Optional[int] = None):
    school_id_val = school_id or _get_school_id()
    with Session(engine) as session:
        room = session.get(models.Room, room_id)
        if not room:
            return

        entries = session.exec(
            select(models.Timetable).where(
                models.Timetable.room_id == room_id,
                models.Timetable.school_id == school_id_val,
                models.Timetable.status == "active",
            )
        ).all()

        for entry in entries:
            teacher = session.get(models.Teacher, entry.teacher_id)
            if teacher:
                await NotificationService.create_and_send(
                    user_id=teacher.user_id,
                    title="Room Changed",
                    message=f"Your room has been changed to {room.room_name} ({room.room_number}).",
                    category="Timetable",
                    priority="high",
                    related_module="timetable",
                    related_record_id=entry.id,
                )


async def notify_emergency_schedule_update(class_id: int, school_id: Optional[int] = None):
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        students = session.exec(
            select(models.Enrollment).where(
                models.Enrollment.class_id == class_id,
                models.Enrollment.school_id == sid,
            )
        ).all()

        for enrollment in students:
            student = session.get(models.Student, enrollment.student_id)
            if student:
                await NotificationService.create_and_send(
                    user_id=student.user_id,
                    title="Emergency Schedule Update",
                    message="The school schedule has been updated due to an emergency. Please check your timetable.",
                    category="Timetable",
                    priority="high",
                    related_module="timetable",
                    related_record_id=class_id,
                )

        teachers_in_class = session.exec(
            select(models.SubjectAllocation).where(
                models.SubjectAllocation.class_id == class_id,
                models.SubjectAllocation.school_id == sid,
            )
        ).all()

        for alloc in teachers_in_class:
            teacher = session.get(models.Teacher, alloc.teacher_id)
            if teacher:
                await NotificationService.create_and_send(
                    user_id=teacher.user_id,
                    title="Emergency Schedule Update",
                    message="The school schedule has been updated due to an emergency. Please check your timetable.",
                    category="Timetable",
                    priority="high",
                    related_module="timetable",
                    related_record_id=class_id,
                )