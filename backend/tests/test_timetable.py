from sqlmodel import Session, select, SQLModel
from app import models, schemas
from app.database import engine
from app.timetable_service import (
    create_timetable_entry,
    validate_timetable_conflicts,
    get_teacher_timetable,
    get_class_timetable,
    get_room_timetable,
    get_student_timetable,
    get_timetable_dashboard,
    get_conflicts,
    resolve_conflict,
    get_period_master,
    create_period_master,
    get_room_allocation,
)

SQLModel.metadata.create_all(engine)


def test_create_and_list_timetable():
    with Session(engine) as session:
        existing = len(session.exec(select(models.Timetable)).all())
        print(f"Existing timetable entries: {existing}")


def test_timetable_conflict_detection():
    with Session(engine) as session:
        sid = session.exec(select(models.School.id)).first()
        if not sid:
            print("No school found, skipping conflict test")
            return

        entry = models.Timetable(
            school_id=sid.id,
            academic_year_id=1,
            class_id=1,
            subject_id=1,
            teacher_id=1,
            day_of_week=0,
            period=1,
            start_time="09:00",
            end_time="09:45",
            status="active",
        )

        conflicts = validate_timetable_conflicts(session, entry, sid.id, exclude_id=None)
        print(f"Conflict detection test: {len(conflicts)} conflicts found")


def test_teacher_timetable():
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher)).first()
        if not teacher:
            print("No teacher found, skipping teacher timetable test")
            return
        entries = get_teacher_timetable(teacher.id)
        print(f"Teacher timetable: {len(entries)} entries for teacher {teacher.id}")


def test_class_timetable():
    with Session(engine) as session:
        class_obj = session.exec(select(models.SchoolClass)).first()
        if not class_obj:
            print("No class found, skipping class timetable test")
            return
        entries = get_class_timetable(class_obj.id)
        print(f"Class timetable: {len(entries)} entries for class {class_obj.id}")


def test_room_timetable():
    with Session(engine) as session:
        room = session.exec(select(models.Room)).first()
        if not room:
            print("No room found, skipping room timetable test")
            return
        entries = get_room_timetable(room.id)
        print(f"Room timetable: {len(entries)} entries for room {room.id}")


def test_timetable_dashboard():
    with Session(engine) as session:
        dashboard = get_timetable_dashboard()
        print(f"Dashboard: total_classes={dashboard['total_classes']}, today_classes={dashboard['today_classes']}")


def test_conflict_log():
    with Session(engine) as session:
        conflicts = get_conflicts(resolved=False)
        print(f"Unresolved conflicts: {len(conflicts)}")


def test_period_master():
    with Session(engine) as session:
        periods = get_period_master()
        print(f"Period master: {len(periods)} periods")


def test_room_allocation():
    with Session(engine) as session:
        allocation = get_room_allocation()
        print(f"Room allocation: {len(allocation)} rooms")


if __name__ == "__main__":
    test_create_and_list_timetable()
    test_timetable_conflict_detection()
    test_teacher_timetable()
    test_class_timetable()
    test_room_timetable()
    test_timetable_dashboard()
    test_conflict_log()
    test_period_master()
    test_room_allocation()
    print("All timetable tests completed.")