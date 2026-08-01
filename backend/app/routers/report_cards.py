"""Report Card Management API Router.

Provides endpoints for:
- CRUD operations on report cards
- Generate/regenerate report cards
- Bulk generation
- PDF download
- QR verification
- Preview
- Grading rules management
"""
import os
import json
import io
import zipfile
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, func, or_
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse, Response

from .. import models, schemas, auth, report_cards as rc_engine
from ..database import engine
from ..tenant import get_current_school_id
from ..pdf_generator import generate_report_card_pdf

router = APIRouter()

REPORT_CARD_PDF_DIR = "static/report_cards"
os.makedirs(REPORT_CARD_PDF_DIR, exist_ok=True)


def _apply_tenant_filter(statement, model):
    """Apply school_id filter to a select statement based on tenant context."""
    sid = get_current_school_id()
    if sid is not None and hasattr(model, "school_id"):
        statement = statement.where(model.school_id == sid)
    return statement


def _get_grading_rules(school_id: int) -> dict:
    """Get active grading rules for a school."""
    with Session(engine) as session:
        rule = session.exec(
            select(models.GradingRule).where(
                models.GradingRule.school_id == school_id,
                models.GradingRule.is_active == True
            )
        ).first()
        if rule:
            return {
                "grading_scale": rule.grading_scale,
                "rules_json": rule.rules_json,
                "pass_percentage": rule.pass_percentage,
            }
    return {
        "grading_scale": "10_point",
        "rules_json": rc_engine.get_default_grade_rules_json(),
        "pass_percentage": 33.0,
    }


def _get_student_enrollment(student_id: int, academic_year_id: int) -> Optional[models.Enrollment]:
    """Get enrollment for a student in an academic year."""
    with Session(engine) as session:
        return session.exec(
            select(models.Enrollment).where(
                models.Enrollment.student_id == student_id,
                models.Enrollment.academic_year_id == academic_year_id,
            )
        ).first()


def _get_attendance_stats(student_id: int, academic_year_id: int) -> dict:
    """Calculate attendance statistics for a student in an academic year."""
    with Session(engine) as session:
        # Get academic year dates
        ac_year = session.get(models.AcademicYear, academic_year_id)
        if not ac_year:
            return {"working_days": 0, "present_days": 0, "percentage": 0.0}

        # Count total attendance records (working days)
        total = session.exec(
            select(func.count(models.Attendance.id)).where(
                models.Attendance.student_id == student_id,
                models.Attendance.date >= ac_year.start_date,
                models.Attendance.date <= ac_year.end_date,
            )
        ).one() or 0

        # Count present days
        present = session.exec(
            select(func.count(models.Attendance.id)).where(
                models.Attendance.student_id == student_id,
                models.Attendance.date >= ac_year.start_date,
                models.Attendance.date <= ac_year.end_date,
                models.Attendance.status == "present",
            )
        ).one() or 0

        return {
            "working_days": total,
            "present_days": present,
            "percentage": rc_engine.calculate_attendance_percentage(present, total),
        }


def _get_student_rank(report_card_id: int, exam_id: int, academic_year_id: int, school_id: int) -> Optional[int]:
    """Calculate rank of a student among all students in the same exam."""
    with Session(engine) as session:
        # Get all report cards for this exam and academic year
        all_cards = session.exec(
            select(models.ReportCard).where(
                models.ReportCard.exam_id == exam_id,
                models.ReportCard.academic_year_id == academic_year_id,
                models.ReportCard.school_id == school_id,
            ).order_by(models.ReportCard.percentage.desc())
        ).all()

        for idx, card in enumerate(all_cards):
            if card.id == report_card_id:
                return idx + 1
    return None


def _build_report_card_data(report_card: models.ReportCard, school: models.School,
                            student: models.Student, user: models.User,
                            exam: models.Exam, ac_year: models.AcademicYear,
                            enrollment: models.Enrollment, subjects_data: List[dict],
                            parent_name: Optional[str] = None,
                            contact_number: Optional[str] = None) -> dict:
    """Build the data dictionary for PDF generation."""
    class_name = ""
    section_name = ""
    if enrollment:
        cls = session_get(models.SchoolClass, enrollment.class_id)
        if cls:
            class_name = cls.name
        if enrollment.section_id:
            sec = session_get(models.Section, enrollment.section_id)
            if sec:
                section_name = sec.name

    # Load SchoolSettings for branding (logo, signature, stamp, principal name)
    principal_name = school.principal_name
    signature_path = None
    stamp_path = None
    logo_path = school.logo
    with Session(engine) as session:
        stmt = select(models.SchoolSettings).where(models.SchoolSettings.school_id == school.id)
        settings = session.exec(stmt).first()
        if settings:
            if settings.logo_path:
                logo_path = settings.logo_path
            if settings.principal_name:
                principal_name = settings.principal_name
            if settings.signature_path:
                signature_path = settings.signature_path
            if settings.stamp_path:
                stamp_path = settings.stamp_path

    return {
        "school_name": school.school_name or "",
        "school_address": school.address or "",
        "school_logo": logo_path if logo_path and os.path.exists(logo_path) else None,
        "school_phone": school.phone or "",
        "school_email": school.email or "",
        "school_website": school.website or "",
        "exam_name": exam.name if exam else "",
        "academic_year_name": ac_year.name if ac_year else "",
        "student_name": user.full_name or "",
        "admission_no": student.admission_no or "",
        "roll_number": str(student.admission_no or ""),
        "class_name": class_name,
        "section_name": section_name,
        "gender": student.gender or "",
        "dob": student.dob,
        "parent_name": parent_name or "",
        "contact_number": contact_number or "",
        "photo_path": student.photo_path if student.photo_path and os.path.exists(student.photo_path) else None,
        "attendance_percentage": report_card.attendance_percentage,
        "working_days": report_card.working_days,
        "present_days": report_card.present_days,
        "subjects": subjects_data,
        "total_marks": report_card.total_marks,
        "obtained_marks": report_card.obtained_marks,
        "percentage": report_card.percentage,
        "overall_grade": report_card.overall_grade or "",
        "gpa": report_card.gpa,
        "result_status": report_card.result_status or "",
        "promotion_status": report_card.promotion_status or "",
        "rank": report_card.rank,
        "teacher_remarks": report_card.teacher_remarks or "",
        "principal_remarks": report_card.principal_remarks or "",
        "verification_id": report_card.verification_id,
        "principal_name": principal_name or "",
        "signature_path": signature_path if signature_path and os.path.exists(signature_path) else None,
        "stamp_path": stamp_path if stamp_path and os.path.exists(stamp_path) else None,
        "verification_base_url": "",
        "generated_on": report_card.generated_on,
    }


def session_get(model_class, id: int):
    """Helper to get a model instance by ID."""
    with Session(engine) as session:
        return session.get(model_class, id)


# ========== GRADING RULES ENDPOINTS ==========


@router.get("/grading-rules", response_model=List[schemas.GradingRuleRead])
def list_grading_rules(current_user: models.User = Depends(auth.get_current_user)):
    """List grading rules for the current school."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        statement = select(models.GradingRule).where(models.GradingRule.school_id == school_id)
        rules = session.exec(statement).all()
        return rules


@router.post("/grading-rules", response_model=schemas.GradingRuleRead)
def create_grading_rule(rule_in: schemas.GradingRuleCreate,
                        current_user: models.User = Depends(auth.get_current_user)):
    """Create a new grading rule for the school."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rule = models.GradingRule(
            school_id=school_id,
            grading_scale=rule_in.grading_scale,
            rules_json=rule_in.rules_json,
            pass_percentage=rule_in.pass_percentage,
            is_active=rule_in.is_active,
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)
        return rule


@router.put("/grading-rules/{rule_id}", response_model=schemas.GradingRuleRead)
def update_grading_rule(rule_id: int, rule_in: schemas.GradingRuleUpdate,
                        current_user: models.User = Depends(auth.get_current_user)):
    """Update a grading rule."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rule = session.get(models.GradingRule, rule_id)
        if not rule or rule.school_id != school_id:
            raise HTTPException(status_code=404, detail="Grading rule not found")

        if rule_in.grading_scale is not None:
            rule.grading_scale = rule_in.grading_scale
        if rule_in.rules_json is not None:
            rule.rules_json = rule_in.rules_json
        if rule_in.pass_percentage is not None:
            rule.pass_percentage = rule_in.pass_percentage
        if rule_in.is_active is not None:
            rule.is_active = rule_in.is_active

        session.add(rule)
        session.commit()
        session.refresh(rule)
        return rule


@router.delete("/grading-rules/{rule_id}")
def delete_grading_rule(rule_id: int, current_user: models.User = Depends(auth.get_current_user)):
    """Delete a grading rule."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rule = session.get(models.GradingRule, rule_id)
        if not rule or rule.school_id != school_id:
            raise HTTPException(status_code=404, detail="Grading rule not found")
        session.delete(rule)
        session.commit()
        return {"message": "Grading rule deleted"}


# ========== REPORT CARD ENDPOINTS ==========


@router.get("/report-cards", response_model=List[schemas.ReportCardRead])
def list_report_cards(
    academic_year_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    section_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    exam_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(auth.get_current_user),
):
    """List report cards with filtering and search."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        statement = select(models.ReportCard).where(models.ReportCard.school_id == school_id)

        if academic_year_id:
            statement = statement.where(models.ReportCard.academic_year_id == academic_year_id)
        if exam_id:
            statement = statement.where(models.ReportCard.exam_id == exam_id)
        if student_id:
            statement = statement.where(models.ReportCard.student_id == student_id)

        # If class/section filter, join with enrollment
        if class_id or section_id:
            statement = statement.join(
                models.Enrollment,
                (models.Enrollment.student_id == models.ReportCard.student_id) &
                (models.Enrollment.academic_year_id == models.ReportCard.academic_year_id)
            )
            if class_id:
                statement = statement.where(models.Enrollment.class_id == class_id)
            if section_id:
                statement = statement.where(models.Enrollment.section_id == section_id)

        # Search by student name
        if search:
            statement = statement.join(
                models.Student,
                models.Student.id == models.ReportCard.student_id
            ).join(
                models.User,
                models.User.id == models.Student.user_id
            ).where(
                models.User.full_name.ilike(f"%{search}%")
            )

        statement = statement.order_by(models.ReportCard.generated_on.desc())
        statement = statement.offset(skip).limit(limit)
        report_cards = session.exec(statement).all()

        result = []
        for rc in report_cards:
            subjects = session.exec(
                select(models.ReportCardSubject).where(
                    models.ReportCardSubject.report_card_id == rc.id
                )
            ).all()
            rc_data = schemas.ReportCardRead.from_orm(rc)
            rc_data.subjects = [schemas.ReportCardSubjectRead.from_orm(s) for s in subjects]
            result.append(rc_data)

        return result


@router.get("/report-cards/{report_card_id}", response_model=schemas.ReportCardRead)
def get_report_card(report_card_id: int,
                    current_user: models.User = Depends(auth.get_current_user)):
    """Get a single report card with subjects."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rc = session.get(models.ReportCard, report_card_id)
        if not rc or rc.school_id != school_id:
            raise HTTPException(status_code=404, detail="Report card not found")

        subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()

        rc_data = schemas.ReportCardRead.from_orm(rc)
        rc_data.subjects = [schemas.ReportCardSubjectRead.from_orm(s) for s in subjects]
        return rc_data


@router.post("/report-cards/generate", response_model=schemas.ReportCardRead)
def generate_report_card(
    req: schemas.ReportCardGenerateRequest,
    current_user: models.User = Depends(auth.get_current_user),
):
    """Generate a report card for a student.

    Validates:
    - Student belongs to the school
    - Exam results exist
    - No duplicate (unless regenerated)
    - Attendance data exists
    """
    school_id = get_current_school_id()
    with Session(engine) as session:
        # Validate student
        student = session.get(models.Student, req.student_id)
        if not student or student.school_id != school_id:
            raise HTTPException(status_code=404, detail="Student not found")

        # Validate exam
        exam = session.get(models.Exam, req.exam_id)
        if not exam or exam.school_id != school_id:
            raise HTTPException(status_code=404, detail="Exam not found")

        # Validate academic year
        ac_year = session.get(models.AcademicYear, req.academic_year_id)
        if not ac_year or ac_year.school_id != school_id:
            raise HTTPException(status_code=404, detail="Academic year not found")

        # Check for existing report card (prevent duplicates)
        existing = session.exec(
            select(models.ReportCard).where(
                models.ReportCard.student_id == req.student_id,
                models.ReportCard.exam_id == req.exam_id,
                models.ReportCard.academic_year_id == req.academic_year_id,
                models.ReportCard.school_id == school_id,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Report card already exists for this student, exam, and academic year. Use regenerate to update."
            )

        # Get exam results for this student
        results = session.exec(
            select(models.ExamResult).where(
                models.ExamResult.exam_id == req.exam_id,
                models.ExamResult.student_id == req.student_id,
                models.ExamResult.school_id == school_id,
            )
        ).all()

        if not results:
            raise HTTPException(status_code=400, detail="No exam results found for this student")

        # Get enrollment
        enrollment = _get_student_enrollment(req.student_id, req.academic_year_id)
        if not enrollment:
            raise HTTPException(status_code=400, detail="Student not enrolled in this academic year")

        # Get attendance
        attendance = _get_attendance_stats(req.student_id, req.academic_year_id)

        # Get grading rules
        grading = _get_grading_rules(school_id)

        # Calculate subject-wise grades
        subjects_data = []
        total_max = 0.0
        total_obtained = 0.0
        subject_grades_for_gpa = []

        for result in results:
            subj = session.get(models.Subject, result.subject_id)
            max_marks = result.max_marks or 100
            obtained = result.marks_obtained or 0
            pct = (obtained / max_marks * 100) if max_marks > 0 else 0

            grade, gp = rc_engine.get_grade_point_for_percentage(pct, grading["rules_json"])

            subjects_data.append({
                "subject_id": result.subject_id,
                "subject_name": subj.name if subj else f"Subject {result.subject_id}",
                "maximum_marks": max_marks,
                "obtained_marks": obtained,
                "percentage": round(pct, 2),
                "grade": grade,
                "grade_point": gp,
                "remarks": "",
            })

            total_max += max_marks
            total_obtained += obtained
            subject_grades_for_gpa.append({"grade_point": gp, "max_marks": max_marks})

        # Calculate totals
        overall_pct = (total_obtained / total_max * 100) if total_max > 0 else 0
        gpa = rc_engine.calculate_gpa(subject_grades_for_gpa, grading["grading_scale"])
        overall_grade = rc_engine.calculate_overall_grade(gpa, grading["grading_scale"])
        result_status = rc_engine.determine_result_status(subjects_data, grading["pass_percentage"])

        # Generate verification ID
        verification_id = rc_engine.generate_verification_id()

        # Create report card
        rc = models.ReportCard(
            school_id=school_id,
            student_id=req.student_id,
            exam_id=req.exam_id,
            academic_year_id=req.academic_year_id,
            total_marks=total_max,
            obtained_marks=total_obtained,
            percentage=round(overall_pct, 2),
            overall_grade=overall_grade,
            gpa=gpa,
            attendance_percentage=attendance["percentage"],
            working_days=attendance["working_days"],
            present_days=attendance["present_days"],
            teacher_remarks=req.teacher_remarks,
            principal_remarks=req.principal_remarks,
            result_status=result_status,
            promotion_status="PROMOTED" if result_status in ("PASS", "PROMOTED") else "DETENTION" if result_status == "DETENTION" else "NOT PROMOTED",
            verification_id=verification_id,
            generated_by=current_user.id,
        )
        session.add(rc)
        session.flush()  # Get ID

        # Create subject records
        for sd in subjects_data:
            rcs = models.ReportCardSubject(
                report_card_id=rc.id,
                subject_id=sd["subject_id"],
                subject_name=sd["subject_name"],
                maximum_marks=sd["maximum_marks"],
                obtained_marks=sd["obtained_marks"],
                percentage=sd["percentage"],
                grade=sd["grade"],
                grade_point=sd["grade_point"],
                remarks=sd["remarks"],
                school_id=school_id,
            )
            session.add(rcs)

        # Calculate rank
        session.flush()
        rank = _get_student_rank(rc.id, req.exam_id, req.academic_year_id, school_id)
        rc.rank = rank

        session.commit()
        session.refresh(rc)

        # Get subjects for response
        subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()

        rc_data = schemas.ReportCardRead.from_orm(rc)
        rc_data.subjects = [schemas.ReportCardSubjectRead.from_orm(s) for s in subjects]
        return rc_data


@router.post("/report-cards/regenerate/{report_card_id}", response_model=schemas.ReportCardRead)
def regenerate_report_card(
    report_card_id: int,
    teacher_remarks: Optional[str] = Query(None),
    principal_remarks: Optional[str] = Query(None),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Regenerate an existing report card with updated data."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rc = session.get(models.ReportCard, report_card_id)
        if not rc or rc.school_id != school_id:
            raise HTTPException(status_code=404, detail="Report card not found")

        # Get fresh exam results
        results = session.exec(
            select(models.ExamResult).where(
                models.ExamResult.exam_id == rc.exam_id,
                models.ExamResult.student_id == rc.student_id,
                models.ExamResult.school_id == school_id,
            )
        ).all()

        if not results:
            raise HTTPException(status_code=400, detail="No exam results found for this student")

        # Get attendance
        attendance = _get_attendance_stats(rc.student_id, rc.academic_year_id)

        # Get grading rules
        grading = _get_grading_rules(school_id)

        # Recalculate
        subjects_data = []
        total_max = 0.0
        total_obtained = 0.0
        subject_grades_for_gpa = []

        for result in results:
            subj = session.get(models.Subject, result.subject_id)
            max_marks = result.max_marks or 100
            obtained = result.marks_obtained or 0
            pct = (obtained / max_marks * 100) if max_marks > 0 else 0

            grade, gp = rc_engine.get_grade_point_for_percentage(pct, grading["rules_json"])

            subjects_data.append({
                "subject_id": result.subject_id,
                "subject_name": subj.name if subj else f"Subject {result.subject_id}",
                "maximum_marks": max_marks,
                "obtained_marks": obtained,
                "percentage": round(pct, 2),
                "grade": grade,
                "grade_point": gp,
                "remarks": "",
            })

            total_max += max_marks
            total_obtained += obtained
            subject_grades_for_gpa.append({"grade_point": gp, "max_marks": max_marks})

        overall_pct = (total_obtained / total_max * 100) if total_max > 0 else 0
        gpa = rc_engine.calculate_gpa(subject_grades_for_gpa, grading["grading_scale"])
        overall_grade = rc_engine.calculate_overall_grade(gpa, grading["grading_scale"])
        result_status = rc_engine.determine_result_status(subjects_data, grading["pass_percentage"])

        # Update report card
        rc.total_marks = total_max
        rc.obtained_marks = total_obtained
        rc.percentage = round(overall_pct, 2)
        rc.overall_grade = overall_grade
        rc.gpa = gpa
        rc.attendance_percentage = attendance["percentage"]
        rc.working_days = attendance["working_days"]
        rc.present_days = attendance["present_days"]
        if teacher_remarks is not None:
            rc.teacher_remarks = teacher_remarks
        if principal_remarks is not None:
            rc.principal_remarks = principal_remarks
        rc.result_status = result_status
        rc.promotion_status = "PROMOTED" if result_status in ("PASS", "PROMOTED") else "DETENTION" if result_status == "DETENTION" else "NOT PROMOTED"
        rc.is_regenerated = True
        rc.generated_by = current_user.id

        # Delete old subject records
        old_subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()
        for s in old_subjects:
            session.delete(s)

        # Create new subject records
        for sd in subjects_data:
            rcs = models.ReportCardSubject(
                report_card_id=rc.id,
                subject_id=sd["subject_id"],
                subject_name=sd["subject_name"],
                maximum_marks=sd["maximum_marks"],
                obtained_marks=sd["obtained_marks"],
                percentage=sd["percentage"],
                grade=sd["grade"],
                grade_point=sd["grade_point"],
                remarks=sd["remarks"],
                school_id=school_id,
            )
            session.add(rcs)

        # Recalculate rank
        rank = _get_student_rank(rc.id, rc.exam_id, rc.academic_year_id, school_id)
        rc.rank = rank

        session.commit()
        session.refresh(rc)

        subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()

        rc_data = schemas.ReportCardRead.from_orm(rc)
        rc_data.subjects = [schemas.ReportCardSubjectRead.from_orm(s) for s in subjects]
        return rc_data


@router.post("/report-cards/bulk-generate")
def bulk_generate_report_cards(
    req: schemas.BulkGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user),
):
    """Bulk generate report cards for multiple students.
    Returns progress tracking info.
    """
    school_id = get_current_school_id()
    results = {"total": len(req.student_ids), "completed": 0, "failed": 0, "errors": [], "report_card_ids": []}

    for student_id in req.student_ids:
        try:
            # Try to generate for each student
            gen_req = schemas.ReportCardGenerateRequest(
                student_id=student_id,
                exam_id=req.exam_id,
                academic_year_id=req.academic_year_id,
                teacher_remarks=req.teacher_remarks,
                principal_remarks=req.principal_remarks,
            )

            # Use the generate function logic inline
            with Session(engine) as session:
                student = session.get(models.Student, student_id)
                if not student or student.school_id != school_id:
                    results["failed"] += 1
                    results["errors"].append(f"Student {student_id}: not found")
                    continue

                exam = session.get(models.Exam, req.exam_id)
                if not exam or exam.school_id != school_id:
                    results["failed"] += 1
                    results["errors"].append(f"Exam {req.exam_id}: not found")
                    continue

                # Check existing
                existing = session.exec(
                    select(models.ReportCard).where(
                        models.ReportCard.student_id == student_id,
                        models.ReportCard.exam_id == req.exam_id,
                        models.ReportCard.academic_year_id == req.academic_year_id,
                        models.ReportCard.school_id == school_id,
                    )
                ).first()
                if existing:
                    results["failed"] += 1
                    results["errors"].append(f"Student {student_id}: report card already exists")
                    continue

                results_data = session.exec(
                    select(models.ExamResult).where(
                        models.ExamResult.exam_id == req.exam_id,
                        models.ExamResult.student_id == student_id,
                        models.ExamResult.school_id == school_id,
                    )
                ).all()

                if not results_data:
                    results["failed"] += 1
                    results["errors"].append(f"Student {student_id}: no exam results")
                    continue

                enrollment = _get_student_enrollment(student_id, req.academic_year_id)
                attendance = _get_attendance_stats(student_id, req.academic_year_id)
                grading = _get_grading_rules(school_id)

                subjects_data = []
                total_max = 0.0
                total_obtained = 0.0
                subject_grades_for_gpa = []

                for result in results_data:
                    subj = session.get(models.Subject, result.subject_id)
                    max_marks = result.max_marks or 100
                    obtained = result.marks_obtained or 0
                    pct = (obtained / max_marks * 100) if max_marks > 0 else 0
                    grade, gp = rc_engine.get_grade_point_for_percentage(pct, grading["rules_json"])

                    subjects_data.append({
                        "subject_id": result.subject_id,
                        "subject_name": subj.name if subj else f"Subject {result.subject_id}",
                        "maximum_marks": max_marks,
                        "obtained_marks": obtained,
                        "percentage": round(pct, 2),
                        "grade": grade,
                        "grade_point": gp,
                        "remarks": "",
                    })
                    total_max += max_marks
                    total_obtained += obtained
                    subject_grades_for_gpa.append({"grade_point": gp, "max_marks": max_marks})

                overall_pct = (total_obtained / total_max * 100) if total_max > 0 else 0
                gpa = rc_engine.calculate_gpa(subject_grades_for_gpa, grading["grading_scale"])
                overall_grade = rc_engine.calculate_overall_grade(gpa, grading["grading_scale"])
                result_status = rc_engine.determine_result_status(subjects_data, grading["pass_percentage"])
                verification_id = rc_engine.generate_verification_id()

                rc = models.ReportCard(
                    school_id=school_id,
                    student_id=student_id,
                    exam_id=req.exam_id,
                    academic_year_id=req.academic_year_id,
                    total_marks=total_max,
                    obtained_marks=total_obtained,
                    percentage=round(overall_pct, 2),
                    overall_grade=overall_grade,
                    gpa=gpa,
                    attendance_percentage=attendance["percentage"],
                    working_days=attendance["working_days"],
                    present_days=attendance["present_days"],
                    teacher_remarks=req.teacher_remarks,
                    principal_remarks=req.principal_remarks,
                    result_status=result_status,
                    promotion_status="PROMOTED" if result_status in ("PASS", "PROMOTED") else "DETENTION" if result_status == "DETENTION" else "NOT PROMOTED",
                    verification_id=verification_id,
                    generated_by=current_user.id,
                )
                session.add(rc)
                session.flush()

                for sd in subjects_data:
                    rcs = models.ReportCardSubject(
                        report_card_id=rc.id,
                        subject_id=sd["subject_id"],
                        subject_name=sd["subject_name"],
                        maximum_marks=sd["maximum_marks"],
                        obtained_marks=sd["obtained_marks"],
                        percentage=sd["percentage"],
                        grade=sd["grade"],
                        grade_point=sd["grade_point"],
                        remarks=sd["remarks"],
                        school_id=school_id,
                    )
                    session.add(rcs)

                rank = _get_student_rank(rc.id, req.exam_id, req.academic_year_id, school_id)
                rc.rank = rank
                session.commit()

                results["completed"] += 1
                results["report_card_ids"].append(rc.id)

        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Student {student_id}: {str(e)}")

    results["status"] = "completed" if results["failed"] == 0 else "partial" if results["completed"] > 0 else "failed"
    return results


@router.get("/report-cards/{report_card_id}/preview", response_model=schemas.ReportCardPreview)
def preview_report_card(report_card_id: int,
                        current_user: models.User = Depends(auth.get_current_user)):
    """Get preview data for a report card."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rc = session.get(models.ReportCard, report_card_id)
        if not rc or rc.school_id != school_id:
            raise HTTPException(status_code=404, detail="Report card not found")

        school = session.get(models.School, school_id)
        student = session.get(models.Student, rc.student_id)
        user = session.get(models.User, student.user_id) if student else None
        exam = session.get(models.Exam, rc.exam_id)
        ac_year = session.get(models.AcademicYear, rc.academic_year_id)
        enrollment = _get_student_enrollment(rc.student_id, rc.academic_year_id)

        subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()

        # Get parent info
        parent_name = None
        contact_number = None
        if student and student.father_id:
            parent = session.get(models.Parent, student.father_id)
            if parent:
                parent_user = session.get(models.User, parent.user_id)
                if parent_user:
                    parent_name = parent_user.full_name
                    contact_number = parent.phone

        class_name = ""
        section_name = ""
        if enrollment:
            cls = session.get(models.SchoolClass, enrollment.class_id)
            if cls:
                class_name = cls.name
            if enrollment.section_id:
                sec = session.get(models.Section, enrollment.section_id)
                if sec:
                    section_name = sec.name

        return schemas.ReportCardPreview(
            school_name=school.school_name if school else "",
            school_address=school.address if school else None,
            school_logo=school.logo if school else None,
            school_phone=school.phone if school else None,
            school_email=school.email if school else None,
            school_website=school.website if school else None,
            exam_name=exam.name if exam else "",
            academic_year_name=ac_year.name if ac_year else "",
            student_name=user.full_name if user else "",
            admission_no=student.admission_no if student else None,
            roll_number=str(student.admission_no or "") if student else None,
            class_name=class_name,
            section_name=section_name or None,
            gender=student.gender if student else None,
            dob=student.dob if student else None,
            parent_name=parent_name,
            contact_number=contact_number,
            photo_path=student.photo_path if student else None,
            attendance_percentage=rc.attendance_percentage,
            working_days=rc.working_days,
            present_days=rc.present_days,
            subjects=[schemas.ReportCardSubjectRead.from_orm(s) for s in subjects],
            total_marks=rc.total_marks,
            obtained_marks=rc.obtained_marks,
            percentage=rc.percentage,
            overall_grade=rc.overall_grade,
            gpa=rc.gpa,
            result_status=rc.result_status,
            promotion_status=rc.promotion_status,
            rank=rc.rank,
            teacher_remarks=rc.teacher_remarks,
            principal_remarks=rc.principal_remarks,
            verification_id=rc.verification_id,
            generated_on=rc.generated_on,
        )


@router.get("/report-cards/{report_card_id}/pdf")
def download_report_card_pdf(report_card_id: int,
                             current_user: models.User = Depends(auth.get_current_user)):
    """Download report card as PDF."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rc = session.get(models.ReportCard, report_card_id)
        if not rc or rc.school_id != school_id:
            raise HTTPException(status_code=404, detail="Report card not found")

        school = session.get(models.School, school_id)
        student = session.get(models.Student, rc.student_id)
        user = session.get(models.User, student.user_id) if student else None
        exam = session.get(models.Exam, rc.exam_id)
        ac_year = session.get(models.AcademicYear, rc.academic_year_id)
        enrollment = _get_student_enrollment(rc.student_id, rc.academic_year_id)

        subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()

        # Get parent info
        parent_name = None
        contact_number = None
        if student and student.father_id:
            parent = session.get(models.Parent, student.father_id)
            if parent:
                parent_user = session.get(models.User, parent.user_id)
                if parent_user:
                    parent_name = parent_user.full_name
                    contact_number = parent.phone

        subjects_data = []
        for s in subjects:
            subjects_data.append({
                "subject_name": s.subject_name or "",
                "maximum_marks": s.maximum_marks,
                "obtained_marks": s.obtained_marks,
                "grade": s.grade or "",
                "grade_point": s.grade_point,
                "remarks": s.remarks or "",
            })

        data = _build_report_card_data(
            rc, school, student, user, exam, ac_year, enrollment,
            subjects_data, parent_name, contact_number
        )

        # Generate PDF
        try:
            pdf_bytes = generate_report_card_pdf(data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

        # Save PDF for caching
        pdf_filename = f"report_card_{rc.id}_{rc.verification_id}.pdf"
        pdf_path = os.path.join(REPORT_CARD_PDF_DIR, pdf_filename)
        try:
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            rc.pdf_path = pdf_path
            session.add(rc)
            session.commit()
        except Exception:
            pass  # Non-critical, PDF still returned

        student_name = (user.full_name or "student").replace(" ", "_")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="report_card_{student_name}.pdf"',
                "Content-Type": "application/pdf",
            }
        )


@router.get("/report-cards/bulk/download")
def bulk_download_report_cards_pdf(
    report_card_ids: str = Query(..., description="Comma-separated list of report card IDs"),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Download multiple report cards as a ZIP file."""
    school_id = get_current_school_id()
    ids = [int(x.strip()) for x in report_card_ids.split(",") if x.strip()]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for rc_id in ids:
            with Session(engine) as session:
                rc = session.get(models.ReportCard, rc_id)
                if not rc or rc.school_id != school_id:
                    continue

                # Try cached PDF first
                if rc.pdf_path and os.path.exists(rc.pdf_path):
                    with open(rc.pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                else:
                    # Generate fresh
                    school = session.get(models.School, school_id)
                    student = session.get(models.Student, rc.student_id)
                    user = session.get(models.User, student.user_id) if student else None
                    exam = session.get(models.Exam, rc.exam_id)
                    ac_year = session.get(models.AcademicYear, rc.academic_year_id)
                    enrollment = _get_student_enrollment(rc.student_id, rc.academic_year_id)
                    subjects = session.exec(
                        select(models.ReportCardSubject).where(
                            models.ReportCardSubject.report_card_id == rc.id
                        )
                    ).all()

                    parent_name = None
                    contact_number = None
                    if student and student.father_id:
                        parent = session.get(models.Parent, student.father_id)
                        if parent:
                            parent_user = session.get(models.User, parent.user_id)
                            if parent_user:
                                parent_name = parent_user.full_name
                                contact_number = parent.phone

                    subjects_data = [{
                        "subject_name": s.subject_name or "",
                        "maximum_marks": s.maximum_marks,
                        "obtained_marks": s.obtained_marks,
                        "grade": s.grade or "",
                        "grade_point": s.grade_point,
                        "remarks": s.remarks or "",
                    } for s in subjects]

                    data = _build_report_card_data(
                        rc, school, student, user, exam, ac_year, enrollment,
                        subjects_data, parent_name, contact_number
                    )
                    pdf_bytes = generate_report_card_pdf(data)

                student_name = (user.full_name or f"student_{rc.student_id}").replace(" ", "_")
                zf.writestr(f"report_card_{student_name}.pdf", pdf_bytes)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=report_cards.zip"},
    )


@router.get("/report-cards/verify/{verification_id}")
def verify_report_card(verification_id: str):
    """Public endpoint to verify a report card via QR code."""
    with Session(engine) as session:
        rc = session.exec(
            select(models.ReportCard).where(
                models.ReportCard.verification_id == verification_id
            )
        ).first()

        if not rc:
            return {
                "valid": False,
                "message": "Invalid Report Card",
                "details": "No report card found with this verification ID.",
            }

        school = session.get(models.School, rc.school_id)
        student = session.get(models.Student, rc.student_id)
        user = session.get(models.User, student.user_id) if student else None
        exam = session.get(models.Exam, rc.exam_id)
        ac_year = session.get(models.AcademicYear, rc.academic_year_id)

        return {
            "valid": True,
            "verified": True,
            "student_name": user.full_name if user else "N/A",
            "class": "",
            "academic_year": ac_year.name if ac_year else "N/A",
            "exam": exam.name if exam else "N/A",
            "issue_date": rc.generated_on.isoformat() if rc.generated_on else "N/A",
            "verification_status": "Verified",
            "school_name": school.school_name if school else "N/A",
            "result_status": rc.result_status,
            "percentage": rc.percentage,
        }


@router.delete("/report-cards/{report_card_id}")
def delete_report_card(report_card_id: int,
                       current_user: models.User = Depends(auth.get_current_user)):
    """Delete a report card and its subjects."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        rc = session.get(models.ReportCard, report_card_id)
        if not rc or rc.school_id != school_id:
            raise HTTPException(status_code=404, detail="Report card not found")

        # Delete subject records
        subjects = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == rc.id
            )
        ).all()
        for s in subjects:
            session.delete(s)

        # Delete PDF if exists
        if rc.pdf_path and os.path.exists(rc.pdf_path):
            try:
                os.remove(rc.pdf_path)
            except Exception:
                pass

        session.delete(rc)
        session.commit()
        return {"message": "Report card deleted"}


@router.get("/report-cards/stats/summary")
def report_card_stats(current_user: models.User = Depends(auth.get_current_user)):
    """Get report card statistics for the school."""
    school_id = get_current_school_id()
    with Session(engine) as session:
        total = session.exec(
            select(func.count(models.ReportCard.id)).where(
                models.ReportCard.school_id == school_id
            )
        ).one() or 0

        passed = session.exec(
            select(func.count(models.ReportCard.id)).where(
                models.ReportCard.school_id == school_id,
                models.ReportCard.result_status.in_(["PASS", "PROMOTED"])
            )
        ).one() or 0

        failed = session.exec(
            select(func.count(models.ReportCard.id)).where(
                models.ReportCard.school_id == school_id,
                models.ReportCard.result_status == "FAIL"
            )
        ).one() or 0

        return {
            "total_report_cards": total,
            "passed": passed,
            "failed": failed,
            "pass_percentage": round((passed / total * 100), 2) if total > 0 else 0,
        }