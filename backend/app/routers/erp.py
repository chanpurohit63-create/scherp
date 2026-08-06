from pathlib import Path
from typing import List, Optional
from datetime import datetime, date
import os
import io
import csv
from sqlmodel import Session, select, func
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from fpdf import FPDF
from sqlalchemy import or_

from .. import models, schemas, crud, auth
from ..database import engine
from ..tenant import get_current_school_id

router = APIRouter()


def verify_child_ownership(student_id: int, current_user: models.User) -> models.Student:
    """Verify that the current user (parent) owns this child AND they belong to the same school.
    Returns the Student object if valid, raises HTTPException(403) otherwise."""
    from sqlmodel import Session, select, or_
    from ..database import engine
    with Session(engine) as session:
        parent = session.exec(
            select(models.Parent).where(models.Parent.user_id == current_user.id)
        ).first()
        if not parent:
            raise HTTPException(status_code=403, detail="Parent profile not found")
        child = session.get(models.Student, student_id)
        if not child:
            raise HTTPException(status_code=404, detail="Student not found")
        # Verify parent-child relationship
        if child.father_id != parent.id and child.mother_id != parent.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this child's data")
        # Verify same school (cross-tenant protection)
        if child.school_id != parent.school_id:
            raise HTTPException(status_code=403, detail="School mismatch - access denied")
        return child


def _apply_tenant_filter(statement, model):
    """Apply school_id filter to a select statement based on tenant context."""
    sid = get_current_school_id()
    if sid is not None and hasattr(model, "school_id"):
        statement = statement.where(model.school_id == sid)
    return statement


ADMIN_ROLES = ("Super Admin", "School Admin", "Principal")
ALL_ADMIN_ROLES = ("Super Admin", "School Admin", "Principal", "Teacher")


def create_resource(resource_in, model, current_user=None):
    resource = model(**resource_in.dict())
    # Explicitly set school_id from current_user to avoid contextvar propagation issues
    if current_user and hasattr(resource, "school_id") and not getattr(resource, "school_id", None):
        resource.school_id = current_user.school_id
    return crud.create_item(resource)


def get_resource(model, resource_id: int):
    return crud.get_item(model, resource_id)


def list_resource(model, skip: int = 0, limit: int = 100):
    return crud.list_items(model, skip=skip, limit=limit)


def update_resource(model, resource_id: int, values: dict):
    return crud.update_item(model, resource_id, values)


def delete_resource(model, resource_id: int):
    return crud.delete_item(model, resource_id)


def make_csv_response(filename: str, headers: List[str], rows: List[List[str]]):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows(rows)
    stream.seek(0)
    return StreamingResponse(
        iter([stream.getvalue().encode('utf-8')]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


def make_certificate_pdf(certificate: models.Certificate, student_name: str = "", school_name: str = ""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, school_name or 'School ERP', ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, certificate.certificate_type.upper(), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'This is to certify that', ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, student_name or f'Student #{certificate.student_id}', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'has been awarded this {certificate.certificate_type.lower()}.', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f'Issue Date: {certificate.issue_date.strftime("%d %B %Y")}', ln=True)
    pdf.ln(5)
    if certificate.remarks:
        pdf.multi_cell(0, 8, f'Remarks: {certificate.remarks}')
    pdf.ln(10)
    pdf.cell(0, 10, f'Certificate ID: {certificate.id}', ln=True, align='R')
    return bytes(pdf.output(dest='S'))


# Parent endpoints
@router.post("/parents", response_model=schemas.ParentRead, status_code=status.HTTP_201_CREATED)
def create_parent(parent_in: schemas.ParentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    parent = create_resource(parent_in, models.Parent, current_user)
    return parent


@router.get("/parents", response_model=List[schemas.ParentRead])
def list_parents(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Parent, skip=skip, limit=limit)


@router.get("/parents/{parent_id}", response_model=schemas.ParentRead)
def get_parent(parent_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    parent = get_resource(models.Parent, parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    return parent


@router.get("/parents/{parent_id}/profile", response_model=schemas.ParentProfileRead)
def get_parent_profile(parent_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        statement = select(models.Parent, models.User).join(models.User, models.Parent.user_id == models.User.id).where(models.Parent.id == parent_id)
        statement = _apply_tenant_filter(statement, models.Parent)
        row = session.exec(statement).first()
        if not row:
            raise HTTPException(status_code=404, detail="Parent not found")
        parent, user = row
        return {
            "id": parent.id,
            "user_id": parent.user_id,
            "phone": parent.phone,
            "address": parent.address,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }


@router.get("/parents/{parent_id}/children", response_model=List[schemas.StudentRead])
def list_parent_children(parent_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        statement = select(models.Student).where(
            or_(models.Student.father_id == parent_id, models.Student.mother_id == parent_id)
        )
        return session.exec(statement).all()


@router.get("/parents/{parent_id}/dashboard")
def parent_dashboard(parent_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        children = session.exec(select(models.Student).where(or_(models.Student.father_id == parent_id, models.Student.mother_id == parent_id))).all()
        result = []
        for child in children:
            present_count = len(session.exec(select(models.Attendance).where(models.Attendance.student_id == child.id, models.Attendance.status == "present")).all())
            absent_count = len(session.exec(select(models.Attendance).where(models.Attendance.student_id == child.id, models.Attendance.status == "absent")).all())
            due_fees = len(session.exec(select(models.FeeAssignment).where(models.FeeAssignment.student_id == child.id, models.FeeAssignment.is_paid == False)).all())
            result.append({
                "student_id": child.id,
                "admission_no": child.admission_no,
                "present_count": present_count,
                "absent_count": absent_count,
                "pending_fee_assignments": due_fees,
            })
        return {"children": result}


@router.delete("/parents/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parent(parent_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Parent, parent_id):
        raise HTTPException(status_code=404, detail="Parent not found")
    return {}


# Teacher endpoints
@router.post("/teachers", response_model=schemas.TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher_in: schemas.TeacherCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    teacher = create_resource(teacher_in, models.Teacher, current_user)
    return teacher


@router.get("/teachers", response_model=List[schemas.TeacherRead])
def list_teachers(
    skip: int = 0,
    limit: int = 20,
    query: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    with Session(engine) as session:
        statement = select(models.Teacher)
        statement = _apply_tenant_filter(statement, models.Teacher)
        if query:
            statement = statement.where(
                or_(
                    models.Teacher.employee_no.contains(query),
                    models.Teacher.hire_date.contains(query),
                )
            )
        if status is not None:
            bool_value = status.lower() == "true"
            statement = statement.where(models.Teacher.is_active == bool_value)
        sort_column = getattr(models.Teacher, sort_by, models.Teacher.id) if sort_by else models.Teacher.id
        if order.lower() == "desc":
            sort_column = sort_column.desc()
        statement = statement.order_by(sort_column).offset(skip).limit(limit)
        return session.exec(statement).all()


@router.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    teacher = get_resource(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.get("/teachers/{teacher_id}/profile", response_model=schemas.TeacherProfileRead)
def get_teacher_profile(teacher_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        statement = select(models.Teacher, models.User).join(models.User, models.Teacher.user_id == models.User.id).where(models.Teacher.id == teacher_id)
        row = session.exec(statement).first()
        if not row:
            raise HTTPException(status_code=404, detail="Teacher not found")
        teacher, user = row
        return {
            "id": teacher.id,
            "user_id": teacher.user_id,
            "employee_no": teacher.employee_no,
            "hire_date": teacher.hire_date,
            "is_active": teacher.is_active,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }


@router.put("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def update_teacher(teacher_id: int, teacher_update: schemas.TeacherUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    teacher = update_resource(models.Teacher, teacher_id, teacher_update.dict(exclude_unset=True))
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Teacher, teacher_id):
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {}


# Student endpoints
@router.post("/students", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student_in: schemas.StudentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    student = create_resource(student_in, models.Student, current_user)
    return student


@router.get("/students", response_model=List[schemas.StudentRead])
def list_students(
    skip: int = 0,
    limit: int = 20,
    query: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
    current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES)),
):
    with Session(engine) as session:
        statement = select(models.Student)
        statement = _apply_tenant_filter(statement, models.Student)
        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                or_(
                    models.Student.admission_no.contains(query),
                    models.Student.gender.contains(query),
                    models.Student.status.contains(query),
                )
            )
        if status:
            statement = statement.where(models.Student.status == status)
        sort_column = getattr(models.Student, sort_by, models.Student.id) if sort_by else models.Student.id
        if order.lower() == "desc":
            sort_column = sort_column.desc()
        statement = statement.order_by(sort_column).offset(skip).limit(limit)
        students = session.exec(statement).all()
        return students


@router.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/students/{student_id}/profile", response_model=schemas.StudentProfileRead)
def get_student_profile(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        statement = select(models.Student, models.User).join(models.User, models.Student.user_id == models.User.id).where(models.Student.id == student_id)
        row = session.exec(statement).first()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        student, user = row
        return {
            "id": student.id,
            "user_id": student.user_id,
            "admission_no": student.admission_no,
            "dob": student.dob,
            "gender": student.gender,
            "admission_date": student.admission_date,
            "status": student.status,
            "father_id": student.father_id,
            "mother_id": student.mother_id,
            "photo_path": student.photo_path,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }


@router.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, student_update: schemas.StudentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    student = update_resource(models.Student, student_id, student_update.dict(exclude_unset=True))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Student, student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {}


@router.post("/students/{student_id}/promote", response_model=schemas.StudentRead)
def promote_student(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.status = "promoted"
    with Session(engine) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


@router.post("/students/{student_id}/transfer-certificate", response_model=schemas.CertificateRead)
def issue_transfer_certificate(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    certificate = models.Certificate(student_id=student_id, certificate_type="Transfer Certificate", remarks="Issued transfer certificate")
    return crud.create_item(certificate)


@router.get("/students/{student_id}/documents", response_model=List[schemas.DocumentRead])
def list_student_documents(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        statement = select(models.Document).where(models.Document.owner_type == "student", models.Document.owner_id == student_id)
        return session.exec(statement).all()


@router.post("/students/{student_id}/documents", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_student_document(student_id: int, file: UploadFile = File(...), current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"student_{student_id}_{file.filename}"
    contents = await file.read()
    file_path.write_bytes(contents)
    document = models.Document(owner_type="student", owner_id=student_id, name=file.filename, file_path=str(file_path))
    return crud.create_item(document)


@router.post("/students/{student_id}/photo", status_code=status.HTTP_200_OK)
async def upload_student_photo(student_id: int, file: UploadFile = File(...), current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"student_photo_{student_id}_{file.filename}"
    contents = await file.read()
    file_path.write_bytes(contents)
    update_resource(models.Student, student_id, {"photo_path": str(file_path)})
    return {"photo_path": str(file_path)}


# Homework submission endpoints
@router.post("/homework-submissions", response_model=schemas.HomeworkSubmissionRead, status_code=status.HTTP_201_CREATED)
def create_homework_submission(submission_in: schemas.HomeworkSubmissionCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    submission = create_resource(submission_in, models.HomeworkSubmission, current_user)
    return submission


@router.get("/homework-submissions", response_model=List[schemas.HomeworkSubmissionRead])
def list_homework_submissions(
    skip: int = 0,
    limit: int = 20,
    query: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))
):
    with Session(engine) as session:
        statement = select(models.HomeworkSubmission)
        statement = _apply_tenant_filter(statement, models.HomeworkSubmission)
        if query:
            statement = statement.where(
                or_(
                    models.HomeworkSubmission.remarks.contains(query),
                    models.HomeworkSubmission.status.contains(query),
                )
            )
        if status:
            statement = statement.where(models.HomeworkSubmission.status == status)
        statement = statement.offset(skip).limit(limit)
        return session.exec(statement).all()


@router.get("/homework-submissions/{submission_id}", response_model=schemas.HomeworkSubmissionRead)
def get_homework_submission(submission_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    submission = get_resource(models.HomeworkSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Homework submission not found")
    return submission


@router.put("/homework-submissions/{submission_id}", response_model=schemas.HomeworkSubmissionRead)
def update_homework_submission(submission_id: int, submission_update: schemas.HomeworkSubmissionUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    submission = update_resource(models.HomeworkSubmission, submission_id, submission_update.dict(exclude_unset=True))
    if not submission:
        raise HTTPException(status_code=404, detail="Homework submission not found")
    return submission


@router.delete("/homework-submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_homework_submission(submission_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.HomeworkSubmission, submission_id):
        raise HTTPException(status_code=404, detail="Homework submission not found")
    return {}


# Teacher attendance endpoints
@router.post("/teacher-attendances", response_model=schemas.TeacherAttendanceRead, status_code=status.HTTP_201_CREATED)
def create_teacher_attendance(attendance_in: schemas.TeacherAttendanceCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    attendance = create_resource(attendance_in, models.TeacherAttendance, current_user)
    return attendance


@router.get("/teacher-attendances", response_model=List[schemas.TeacherAttendanceRead])
def list_teacher_attendances(
    skip: int = 0,
    limit: int = 20,
    query: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))
):
    with Session(engine) as session:
        statement = select(models.TeacherAttendance)
        statement = _apply_tenant_filter(statement, models.TeacherAttendance)
        if query:
            statement = statement.where(models.TeacherAttendance.remarks.contains(query))
        if status:
            statement = statement.where(models.TeacherAttendance.status == status)
        statement = statement.offset(skip).limit(limit)
        return session.exec(statement).all()


@router.get("/teacher-attendances/{attendance_id}", response_model=schemas.TeacherAttendanceRead)
def get_teacher_attendance(attendance_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    attendance = get_resource(models.TeacherAttendance, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Teacher attendance not found")
    return attendance


@router.put("/teacher-attendances/{attendance_id}", response_model=schemas.TeacherAttendanceRead)
def update_teacher_attendance(attendance_id: int, attendance_update: schemas.TeacherAttendanceUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    attendance = update_resource(models.TeacherAttendance, attendance_id, attendance_update.dict(exclude_unset=True))
    if not attendance:
        raise HTTPException(status_code=404, detail="Teacher attendance not found")
    return attendance


@router.delete("/teacher-attendances/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher_attendance(attendance_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.TeacherAttendance, attendance_id):
        raise HTTPException(status_code=404, detail="Teacher attendance not found")
    return {}


# Academic year endpoints
@router.post("/academic-years", response_model=schemas.AcademicYearRead, status_code=status.HTTP_201_CREATED)
def create_academic_year(year_in: schemas.AcademicYearCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    year = create_resource(year_in, models.AcademicYear, current_user)
    return year


@router.get("/academic-years", response_model=List[schemas.AcademicYearRead])
def list_academic_years(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.AcademicYear, skip=skip, limit=limit)


@router.get("/academic-years/{year_id}", response_model=schemas.AcademicYearRead)
def get_academic_year(year_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    year = get_resource(models.AcademicYear, year_id)
    if not year:
        raise HTTPException(status_code=404, detail="Academic year not found")
    return year


@router.put("/academic-years/{year_id}", response_model=schemas.AcademicYearRead)
def update_academic_year(year_id: int, year_update: schemas.AcademicYearUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    year = update_resource(models.AcademicYear, year_id, year_update.dict(exclude_unset=True))
    if not year:
        raise HTTPException(status_code=404, detail="Academic year not found")
    return year


@router.delete("/academic-years/{year_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_academic_year(year_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.AcademicYear, year_id):
        raise HTTPException(status_code=404, detail="Academic year not found")
    return {}


# Class endpoints
@router.post("/classes", response_model=schemas.SchoolClassRead, status_code=status.HTTP_201_CREATED)
def create_class(class_in: schemas.SchoolClassCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    school_class = create_resource(class_in, models.SchoolClass, current_user)
    return school_class


@router.get("/classes", response_model=List[schemas.SchoolClassRead])
def list_classes(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.SchoolClass, skip=skip, limit=limit)


@router.get("/classes/{class_id}", response_model=schemas.SchoolClassRead)
def get_class(class_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    school_class = get_resource(models.SchoolClass, class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return school_class


@router.put("/classes/{class_id}", response_model=schemas.SchoolClassRead)
def update_class(class_id: int, class_update: schemas.SchoolClassUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    school_class = update_resource(models.SchoolClass, class_id, class_update.dict(exclude_unset=True))
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return school_class


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(class_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.SchoolClass, class_id):
        raise HTTPException(status_code=404, detail="Class not found")
    return {}


# Section endpoints
@router.post("/sections", response_model=schemas.SectionRead, status_code=status.HTTP_201_CREATED)
def create_section(section_in: schemas.SectionCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    section = create_resource(section_in, models.Section, current_user)
    return section


@router.get("/sections", response_model=List[schemas.SectionRead])
def list_sections(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Section, skip=skip, limit=limit)


@router.get("/sections/{section_id}", response_model=schemas.SectionRead)
def get_section(section_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    section = get_resource(models.Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@router.put("/sections/{section_id}", response_model=schemas.SectionRead)
def update_section(section_id: int, section_update: schemas.SectionUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    section = update_resource(models.Section, section_id, section_update.dict(exclude_unset=True))
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(section_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Section, section_id):
        raise HTTPException(status_code=404, detail="Section not found")
    return {}


# Subject endpoints
@router.post("/subjects", response_model=schemas.SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(subject_in: schemas.SubjectCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    subject = create_resource(subject_in, models.Subject, current_user)
    return subject


@router.get("/subjects", response_model=List[schemas.SubjectRead])
def list_subjects(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Subject, skip=skip, limit=limit)


@router.get("/subjects/{subject_id}", response_model=schemas.SubjectRead)
def get_subject(subject_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    subject = get_resource(models.Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/subjects/{subject_id}", response_model=schemas.SubjectRead)
def update_subject(subject_id: int, subject_update: schemas.SubjectUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    subject = update_resource(models.Subject, subject_id, subject_update.dict(exclude_unset=True))
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Subject, subject_id):
        raise HTTPException(status_code=404, detail="Subject not found")
    return {}


# Room endpoints
@router.post("/rooms", response_model=schemas.RoomRead, status_code=status.HTTP_201_CREATED)
def create_room(room_in: schemas.RoomCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    with Session(engine) as session:
        sid = current_user.school_id
        if sid is not None:
            existing = session.exec(
                select(models.Room).where(
                    models.Room.school_id == sid,
                    models.Room.room_name == room_in.room_name,
                )
            ).first()
            if existing:
                raise HTTPException(status_code=409, detail="Room with this name already exists")
        room = models.Room(**room_in.dict())
        room.school_id = sid
        session.add(room)
        session.commit()
        session.refresh(room)
        return room


@router.get("/rooms", response_model=List[schemas.RoomRead])
def list_rooms(
    skip: int = 0,
    limit: int = 100,
    room_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES)),
):
    with Session(engine) as session:
        statement = select(models.Room)
        statement = _apply_tenant_filter(statement, models.Room)
        if room_type:
            statement = statement.where(models.Room.room_type == room_type)
        if is_active is not None:
            statement = statement.where(models.Room.is_active == is_active)
        statement = statement.order_by(models.Room.id).offset(skip).limit(limit)
        return session.exec(statement).all()


@router.get("/rooms/{room_id}", response_model=schemas.RoomRead)
def get_room(room_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    room = get_resource(models.Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.put("/rooms/{room_id}", response_model=schemas.RoomRead)
def update_room(room_id: int, room_update: schemas.RoomUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    room = update_resource(models.Room, room_id, room_update.dict(exclude_unset=True))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Room, room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    return {}


# Subject allocation endpoints
@router.post("/subject-allocations", response_model=schemas.SubjectAllocationRead, status_code=status.HTTP_201_CREATED)
def create_subject_allocation(allocation_in: schemas.SubjectAllocationCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    allocation = create_resource(allocation_in, models.SubjectAllocation, current_user)
    return allocation


@router.get("/subject-allocations", response_model=List[schemas.SubjectAllocationRead])
def list_subject_allocations(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.SubjectAllocation, skip=skip, limit=limit)


@router.get("/subject-allocations/{allocation_id}", response_model=schemas.SubjectAllocationRead)
def get_subject_allocation(allocation_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    allocation = get_resource(models.SubjectAllocation, allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Subject allocation not found")
    return allocation


@router.put("/subject-allocations/{allocation_id}", response_model=schemas.SubjectAllocationRead)
def update_subject_allocation(allocation_id: int, allocation_update: schemas.SubjectAllocationUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    allocation = update_resource(models.SubjectAllocation, allocation_id, allocation_update.dict(exclude_unset=True))
    if not allocation:
        raise HTTPException(status_code=404, detail="Subject allocation not found")
    return allocation


@router.delete("/subject-allocations/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject_allocation(allocation_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.SubjectAllocation, allocation_id):
        raise HTTPException(status_code=404, detail="Subject allocation not found")
    return {}


# Enrollment endpoints
@router.post("/enrollments", response_model=schemas.EnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment_in: schemas.EnrollmentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    enrollment = create_resource(enrollment_in, models.Enrollment, current_user)
    return enrollment


@router.get("/enrollments", response_model=List[schemas.EnrollmentRead])
def list_enrollments(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Enrollment, skip=skip, limit=limit)


@router.get("/enrollments/{enrollment_id}", response_model=schemas.EnrollmentRead)
def get_enrollment(enrollment_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    enrollment = get_resource(models.Enrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.put("/enrollments/{enrollment_id}", response_model=schemas.EnrollmentRead)
def update_enrollment(enrollment_id: int, enrollment_update: schemas.EnrollmentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    enrollment = update_resource(models.Enrollment, enrollment_id, enrollment_update.dict(exclude_unset=True))
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Enrollment, enrollment_id):
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {}


# Attendance endpoints
@router.post("/attendances", response_model=schemas.AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance_in: schemas.AttendanceCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    attendance = create_resource(attendance_in, models.Attendance, current_user)
    return attendance


@router.get("/attendances", response_model=List[schemas.AttendanceRead])
def list_attendances(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    return list_resource(models.Attendance, skip=skip, limit=limit)


@router.get("/attendances/{attendance_id}", response_model=schemas.AttendanceRead)
def get_attendance(attendance_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    attendance = get_resource(models.Attendance, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@router.put("/attendances/{attendance_id}", response_model=schemas.AttendanceRead)
def update_attendance(attendance_id: int, attendance_update: schemas.AttendanceUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    attendance = update_resource(models.Attendance, attendance_id, attendance_update.dict(exclude_unset=True))
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@router.delete("/attendances/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(attendance_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Attendance, attendance_id):
        raise HTTPException(status_code=404, detail="Attendance not found")
    return {}


# Homework endpoints
@router.post("/homeworks", response_model=schemas.HomeworkRead, status_code=status.HTTP_201_CREATED)
def create_homework(homework_in: schemas.HomeworkCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    homework = create_resource(homework_in, models.Homework, current_user)
    return homework


@router.get("/homeworks", response_model=List[schemas.HomeworkRead])
def list_homeworks(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    return list_resource(models.Homework, skip=skip, limit=limit)


@router.get("/homeworks/{homework_id}", response_model=schemas.HomeworkRead)
def get_homework(homework_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    homework = get_resource(models.Homework, homework_id)
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    return homework


@router.put("/homeworks/{homework_id}", response_model=schemas.HomeworkRead)
def update_homework(homework_id: int, homework_update: schemas.HomeworkUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    homework = update_resource(models.Homework, homework_id, homework_update.dict(exclude_unset=True))
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    return homework


@router.delete("/homeworks/{homework_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_homework(homework_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Homework, homework_id):
        raise HTTPException(status_code=404, detail="Homework not found")
    return {}


# Exam endpoints
@router.post("/exams", response_model=schemas.ExamRead, status_code=status.HTTP_201_CREATED)
def create_exam(exam_in: schemas.ExamCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    exam = create_resource(exam_in, models.Exam, current_user)
    return exam


@router.get("/exams", response_model=List[schemas.ExamRead])
def list_exams(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Exam, skip=skip, limit=limit)


@router.get("/exams/{exam_id}", response_model=schemas.ExamRead)
def get_exam(exam_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    exam = get_resource(models.Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.put("/exams/{exam_id}", response_model=schemas.ExamRead)
def update_exam(exam_id: int, exam_update: schemas.ExamUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    exam = update_resource(models.Exam, exam_id, exam_update.dict(exclude_unset=True))
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Exam, exam_id):
        raise HTTPException(status_code=404, detail="Exam not found")
    return {}


# Exam result endpoints
@router.post("/exam-results", response_model=schemas.ExamResultRead, status_code=status.HTTP_201_CREATED)
def create_exam_result(result_in: schemas.ExamResultCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    result = create_resource(result_in, models.ExamResult, current_user)
    return result


@router.get("/exam-results", response_model=List[schemas.ExamResultRead])
def list_exam_results(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.ExamResult, skip=skip, limit=limit)


@router.get("/exam-results/{result_id}", response_model=schemas.ExamResultRead)
def get_exam_result(result_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    result = get_resource(models.ExamResult, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Exam result not found")
    return result


@router.put("/exam-results/{result_id}", response_model=schemas.ExamResultRead)
def update_exam_result(result_id: int, result_update: schemas.ExamResultUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    result = update_resource(models.ExamResult, result_id, result_update.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Exam result not found")
    return result


@router.delete("/exam-results/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_result(result_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.ExamResult, result_id):
        raise HTTPException(status_code=404, detail="Exam result not found")
    return {}


# Fee structure endpoints
@router.post("/fee-structures", response_model=schemas.FeeStructureRead, status_code=status.HTTP_201_CREATED)
def create_fee_structure(fee_structure_in: schemas.FeeStructureCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    fee_structure = create_resource(fee_structure_in, models.FeeStructure, current_user)
    return fee_structure


@router.get("/fee-structures", response_model=List[schemas.FeeStructureRead])
def list_fee_structures(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.FeeStructure, skip=skip, limit=limit)


@router.get("/fee-structures/{fee_structure_id}", response_model=schemas.FeeStructureRead)
def get_fee_structure(fee_structure_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    fee_structure = get_resource(models.FeeStructure, fee_structure_id)
    if not fee_structure:
        raise HTTPException(status_code=404, detail="Fee structure not found")
    return fee_structure


@router.put("/fee-structures/{fee_structure_id}", response_model=schemas.FeeStructureRead)
def update_fee_structure(fee_structure_id: int, fee_structure_update: schemas.FeeStructureUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    fee_structure = update_resource(models.FeeStructure, fee_structure_id, fee_structure_update.dict(exclude_unset=True))
    if not fee_structure:
        raise HTTPException(status_code=404, detail="Fee structure not found")
    return fee_structure


@router.delete("/fee-structures/{fee_structure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_structure(fee_structure_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.FeeStructure, fee_structure_id):
        raise HTTPException(status_code=404, detail="Fee structure not found")
    return {}


# Fee assignment endpoints
@router.post("/fee-assignments", response_model=schemas.FeeAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_fee_assignment(fee_assignment_in: schemas.FeeAssignmentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    assignment = create_resource(fee_assignment_in, models.FeeAssignment, current_user)
    return assignment


@router.get("/fee-assignments", response_model=List[schemas.FeeAssignmentRead])
def list_fee_assignments(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.FeeAssignment, skip=skip, limit=limit)


@router.get("/fee-assignments/{assignment_id}", response_model=schemas.FeeAssignmentRead)
def get_fee_assignment(assignment_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    assignment = get_resource(models.FeeAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Fee assignment not found")
    return assignment


@router.put("/fee-assignments/{assignment_id}", response_model=schemas.FeeAssignmentRead)
def update_fee_assignment(assignment_id: int, assignment_update: schemas.FeeAssignmentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    assignment = update_resource(models.FeeAssignment, assignment_id, assignment_update.dict(exclude_unset=True))
    if not assignment:
        raise HTTPException(status_code=404, detail="Fee assignment not found")
    return assignment


@router.delete("/fee-assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_assignment(assignment_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.FeeAssignment, assignment_id):
        raise HTTPException(status_code=404, detail="Fee assignment not found")
    return {}


# Payment endpoints
@router.post("/payments", response_model=schemas.PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(payment_in: schemas.PaymentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    payment = create_resource(payment_in, models.Payment, current_user)
    return payment


@router.get("/payments", response_model=List[schemas.PaymentRead])
def list_payments(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Payment, skip=skip, limit=limit)


@router.get("/payments/{payment_id}", response_model=schemas.PaymentRead)
def get_payment(payment_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    payment = get_resource(models.Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.put("/payments/{payment_id}", response_model=schemas.PaymentRead)
def update_payment(payment_id: int, payment_update: schemas.PaymentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    payment = update_resource(models.Payment, payment_id, payment_update.dict(exclude_unset=True))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Payment, payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")
    return {}


# Notice endpoints
@router.post("/notices", response_model=schemas.NoticeRead, status_code=status.HTTP_201_CREATED)
def create_notice(notice_in: schemas.NoticeCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    notice = create_resource(notice_in, models.Notice, current_user)
    return notice


@router.get("/notices", response_model=List[schemas.NoticeRead])
def list_notices(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    return list_resource(models.Notice, skip=skip, limit=limit)


@router.get("/notices/{notice_id}", response_model=schemas.NoticeRead)
def get_notice(notice_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    notice = get_resource(models.Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice


@router.put("/notices/{notice_id}", response_model=schemas.NoticeRead)
def update_notice(notice_id: int, notice_update: schemas.NoticeUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    notice = update_resource(models.Notice, notice_id, notice_update.dict(exclude_unset=True))
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice


@router.delete("/notices/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notice(notice_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Notice, notice_id):
        raise HTTPException(status_code=404, detail="Notice not found")
    return {}


# Message endpoints
@router.post("/messages", response_model=schemas.MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(message_in: schemas.MessageCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    message = create_resource(message_in, models.Message, current_user)
    return message


@router.get("/messages", response_model=List[schemas.MessageRead])
def list_messages(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    return list_resource(models.Message, skip=skip, limit=limit)


@router.get("/messages/{message_id}", response_model=schemas.MessageRead)
def get_message(message_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    message = get_resource(models.Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.put("/messages/{message_id}", response_model=schemas.MessageRead)
def update_message(message_id: int, message_update: schemas.MessageUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    message = update_resource(models.Message, message_id, message_update.dict(exclude_unset=True))
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    if not delete_resource(models.Message, message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    return {}


# Event endpoints
@router.post("/events", response_model=schemas.EventRead, status_code=status.HTTP_201_CREATED)
def create_event(event_in: schemas.EventCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    event = create_resource(event_in, models.Event, current_user)
    return event


@router.get("/events", response_model=List[schemas.EventRead])
def list_events(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    return list_resource(models.Event, skip=skip, limit=limit)


@router.get("/events/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    event = get_resource(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/events/{event_id}", response_model=schemas.EventRead)
def update_event(event_id: int, event_update: schemas.EventUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    event = update_resource(models.Event, event_id, event_update.dict(exclude_unset=True))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    if not delete_resource(models.Event, event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {}


# Certificate endpoints
@router.post("/certificates", response_model=schemas.CertificateRead, status_code=status.HTTP_201_CREATED)
def create_certificate(certificate_in: schemas.CertificateCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    certificate = create_resource(certificate_in, models.Certificate, current_user)
    return certificate


@router.get("/certificates", response_model=List[schemas.CertificateRead])
def list_certificates(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Certificate, skip=skip, limit=limit)


@router.get("/certificates/{certificate_id}", response_model=schemas.CertificateRead)
def get_certificate(certificate_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    certificate = get_resource(models.Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate


@router.put("/certificates/{certificate_id}", response_model=schemas.CertificateRead)
def update_certificate(certificate_id: int, certificate_update: schemas.CertificateUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    certificate = update_resource(models.Certificate, certificate_id, certificate_update.dict(exclude_unset=True))
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate


@router.delete("/certificates/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(certificate_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Certificate, certificate_id):
        raise HTTPException(status_code=404, detail="Certificate not found")
    return {}


# Document endpoints
@router.post("/documents", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(document_in: schemas.DocumentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    document = create_resource(document_in, models.Document, current_user)
    return document


@router.get("/documents", response_model=List[schemas.DocumentRead])
def list_documents(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Document, skip=skip, limit=limit)


@router.get("/documents/{document_id}", response_model=schemas.DocumentRead)
def get_document(document_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    document = get_resource(models.Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/documents/{document_id}", response_model=schemas.DocumentRead)
def update_document(document_id: int, document_update: schemas.DocumentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    document = update_resource(models.Document, document_id, document_update.dict(exclude_unset=True))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Document, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {}


# ========== DASHBOARD ==========
@router.get("/dashboard/summary", response_model=schemas.DashboardSummaryRead)
def get_dashboard_summary(current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    with Session(engine) as session:
        sid = get_current_school_id()
        
        # Tenant-filtered queries
        student_stmt = select(func.count(models.Student.id))
        teacher_stmt = select(func.count(models.Teacher.id))
        attendance_stmt = select(func.count(models.Attendance.id))
        present_stmt = select(func.count(models.Attendance.id)).where(models.Attendance.status == "present")
        payment_sum_stmt = select(func.coalesce(func.sum(models.Payment.amount), 0))
        pending_fees_stmt = select(func.count(models.FeeAssignment.id)).where(models.FeeAssignment.is_paid == False)
        exam_stmt = select(func.count(models.Exam.id)).where(models.Exam.start_date >= datetime.utcnow().date())
        event_stmt = select(func.count(models.Event.id)).where(models.Event.start_date >= datetime.utcnow())
        notices_stmt = select(models.Notice).order_by(models.Notice.created_on.desc()).limit(5)
        
        if sid is not None:
            student_stmt = student_stmt.where(models.Student.school_id == sid)
            teacher_stmt = teacher_stmt.where(models.Teacher.school_id == sid)
            attendance_stmt = attendance_stmt.where(models.Attendance.school_id == sid)
            present_stmt = present_stmt.where(models.Attendance.school_id == sid)
            payment_sum_stmt = payment_sum_stmt.where(models.Payment.school_id == sid)
            pending_fees_stmt = pending_fees_stmt.where(models.FeeAssignment.school_id == sid)
            exam_stmt = exam_stmt.where(models.Exam.school_id == sid)
            event_stmt = event_stmt.where(models.Event.school_id == sid)
            notices_stmt = notices_stmt.where(models.Notice.school_id == sid)
        
        total_students = session.exec(student_stmt).one()
        total_teachers = session.exec(teacher_stmt).one()
        total_attendance = session.exec(attendance_stmt).one()
        present_attendance = session.exec(present_stmt).one()
        attendance_pct = round((present_attendance / total_attendance * 100), 2) if total_attendance else 0.0
        fee_collection = session.exec(payment_sum_stmt).one()
        pending_fees = session.exec(pending_fees_stmt).one()
        upcoming_exams = session.exec(exam_stmt).one()
        upcoming_events = session.exec(event_stmt).one()
        notices_list = session.exec(notices_stmt).all()

        monthly_attendance = []
        for m in range(1, 13):
            cnt = session.exec(
                select(func.count(models.Attendance.id)).where(
                    func.extract('month', models.Attendance.date) == m,
                    models.Attendance.status == "present",
                    models.Attendance.school_id == sid if sid is not None else True
                )
            ).one()
            monthly_attendance.append({"month": m, "count": cnt})

        monthly_fee = []
        for m in range(1, 13):
            fee_stmt = select(func.coalesce(func.sum(models.Payment.amount), 0)).where(
                func.extract('month', models.Payment.paid_on) == m
            )
            if sid is not None:
                fee_stmt = fee_stmt.where(models.Payment.school_id == sid)
            total = session.exec(fee_stmt).one()
            monthly_fee.append({"month": m, "total": float(total)})

        student_growth = []
        for m in range(1, 13):
            growth_stmt = select(func.count(models.Student.id)).where(
                func.extract('month', models.Student.admission_date) == m
            )
            if sid is not None:
                growth_stmt = growth_stmt.where(models.Student.school_id == sid)
            cnt = session.exec(growth_stmt).one()
            student_growth.append({"month": m, "count": cnt})

        exam_performance = []
        exam_list_stmt = select(models.Exam).limit(5)
        if sid is not None:
            exam_list_stmt = exam_list_stmt.where(models.Exam.school_id == sid)
        exams = session.exec(exam_list_stmt).all()
        for exam in exams:
            avg_stmt = select(func.avg(models.ExamResult.marks_obtained)).where(models.ExamResult.exam_id == exam.id)
            if sid is not None:
                avg_stmt = avg_stmt.where(models.ExamResult.school_id == sid)
            avg_marks = session.exec(avg_stmt).one()
            exam_performance.append({"exam_name": exam.name, "average_marks": round(float(avg_marks or 0), 2)})

        return schemas.DashboardSummaryRead(
            total_students=total_students or 0,
            total_teachers=total_teachers or 0,
            attendance_percentage=attendance_pct,
            fee_collection=float(fee_collection or 0),
            pending_fees=pending_fees or 0,
            upcoming_exams=upcoming_exams or 0,
            upcoming_events=upcoming_events or 0,
            notices=notices_list,
            monthly_attendance=monthly_attendance,
            monthly_fee_collection=monthly_fee,
            student_growth=student_growth,
            exam_performance=exam_performance,
        )


# ========== REPORTS ==========
@router.get("/reports/students")
def report_students(
    skip: int = 0, limit: int = 100, query: Optional[str] = None,
    status: Optional[str] = None, export: Optional[str] = None,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    with Session(engine) as session:
        sid = get_current_school_id()
        statement = select(models.Student, models.User).join(models.User, models.Student.user_id == models.User.id)
        if sid is not None:
            statement = statement.where(models.Student.school_id == sid)
        if query:
            statement = statement.where(models.User.full_name.contains(query))
        if status:
            statement = statement.where(models.Student.status == status)
        rows = session.exec(statement.offset(skip).limit(limit)).all()
        data = []
        for student, user in rows:
            data.append({
                "id": student.id, "admission_no": student.admission_no,
                "full_name": user.full_name, "email": user.email,
                "gender": student.gender, "status": student.status,
            })
        if export == "csv":
            headers = ["ID", "Admission No", "Name", "Email", "Gender", "Status"]
            rows_csv = [[str(r["id"]), r["admission_no"] or "", r["full_name"] or "", r["email"], r["gender"] or "", r["status"]] for r in data]
            return make_csv_response("students_report.csv", headers, rows_csv)
        return data


@router.get("/reports/attendance")
def report_attendance(
    skip: int = 0, limit: int = 100, from_date: Optional[date] = None,
    to_date: Optional[date] = None, status_filter: Optional[str] = None,
    export: Optional[str] = None, current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    with Session(engine) as session:
        sid = get_current_school_id()
        statement = select(models.Attendance, models.Student).join(models.Student, models.Attendance.student_id == models.Student.id)
        if sid is not None:
            statement = statement.where(models.Attendance.school_id == sid)
        if from_date:
            statement = statement.where(models.Attendance.date >= from_date)
        if to_date:
            statement = statement.where(models.Attendance.date <= to_date)
        if status_filter:
            statement = statement.where(models.Attendance.status == status_filter)
        rows = session.exec(statement.offset(skip).limit(limit)).all()
        data = []
        for att, stu in rows:
            data.append({
                "id": att.id, "student_id": att.student_id,
                "date": str(att.date), "status": att.status,
                "remarks": att.remarks, "admission_no": stu.admission_no,
            })
        if export == "csv":
            headers = ["ID", "Student ID", "Date", "Status", "Remarks", "Admission No"]
            rows_csv = [[str(r["id"]), str(r["student_id"]), r["date"], r["status"], r["remarks"] or "", r["admission_no"] or ""] for r in data]
            return make_csv_response("attendance_report.csv", headers, rows_csv)
        return data


@router.get("/reports/teachers")
def report_teachers(
    skip: int = 0, limit: int = 100, query: Optional[str] = None,
    export: Optional[str] = None, current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    with Session(engine) as session:
        sid = get_current_school_id()
        statement = select(models.Teacher, models.User).join(models.User, models.Teacher.user_id == models.User.id)
        if sid is not None:
            statement = statement.where(models.Teacher.school_id == sid)
        if query:
            statement = statement.where(models.User.full_name.contains(query))
        rows = session.exec(statement.offset(skip).limit(limit)).all()
        data = []
        for teacher, user in rows:
            data.append({
                "id": teacher.id, "employee_no": teacher.employee_no,
                "full_name": user.full_name, "email": user.email,
                "hire_date": str(teacher.hire_date or ""), "is_active": teacher.is_active,
            })
        if export == "csv":
            headers = ["ID", "Employee No", "Name", "Email", "Hire Date", "Active"]
            rows_csv = [[str(r["id"]), r["employee_no"] or "", r["full_name"] or "", r["email"], r["hire_date"], str(r["is_active"])] for r in data]
            return make_csv_response("teachers_report.csv", headers, rows_csv)
        return data


@router.get("/reports/fees")
def report_fees(
    skip: int = 0, limit: int = 100, is_paid: Optional[bool] = None,
    export: Optional[str] = None, current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    with Session(engine) as session:
        sid = get_current_school_id()
        statement = select(models.FeeAssignment).join(models.FeeStructure, models.FeeAssignment.fee_structure_id == models.FeeStructure.id)
        if sid is not None:
            statement = statement.where(models.FeeAssignment.school_id == sid)
        if is_paid is not None:
            statement = statement.where(models.FeeAssignment.is_paid == is_paid)
        rows = session.exec(statement.offset(skip).limit(limit)).all()
        data = []
        for fa in rows:
            data.append({
                "id": fa.id, "student_id": fa.student_id,
                "due_date": str(fa.due_date or ""), "is_paid": fa.is_paid,
            })
        if export == "csv":
            headers = ["ID", "Student ID", "Due Date", "Paid"]
            rows_csv = [[str(r["id"]), str(r["student_id"]), r["due_date"], str(r["is_paid"])] for r in data]
            return make_csv_response("fees_report.csv", headers, rows_csv)
        return data


@router.get("/reports/exams")
def report_exams(
    skip: int = 0, limit: int = 100, exam_id: Optional[int] = None,
    export: Optional[str] = None, current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    with Session(engine) as session:
        sid = get_current_school_id()
        statement = select(models.ExamResult, models.Student).join(models.Student, models.ExamResult.student_id == models.Student.id)
        if sid is not None:
            statement = statement.where(models.ExamResult.school_id == sid)
        if exam_id:
            statement = statement.where(models.ExamResult.exam_id == exam_id)
        rows = session.exec(statement.offset(skip).limit(limit)).all()
        data = []
        for er, stu in rows:
            data.append({
                "id": er.id, "exam_id": er.exam_id, "student_id": er.student_id,
                "subject_id": er.subject_id, "marks_obtained": er.marks_obtained,
                "max_marks": er.max_marks, "admission_no": stu.admission_no,
            })
        if export == "csv":
            headers = ["ID", "Exam ID", "Student ID", "Subject ID", "Marks", "Max Marks", "Admission No"]
            rows_csv = [[str(r["id"]), str(r["exam_id"]), str(r["student_id"]), str(r["subject_id"]), str(r["marks_obtained"] or ""), str(r["max_marks"] or ""), r["admission_no"] or ""] for r in data]
            return make_csv_response("exams_report.csv", headers, rows_csv)
        return data


# ========== CERTIFICATE PDF ==========
@router.post("/certificates/generate", response_model=schemas.CertificateRead, status_code=status.HTTP_201_CREATED)
def generate_certificate(
    certificate_type: str = Query(...),
    student_id: int = Query(...),
    remarks: Optional[str] = None,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    with Session(engine) as session:
        user = session.get(models.User, student.user_id)
    school_name = "School ERP"
    settings = crud.get_item(models.SchoolSettings, 1)
    if settings and settings.school_name:
        school_name = settings.school_name
    certificate = models.Certificate(
        student_id=student_id, certificate_type=certificate_type,
        remarks=remarks or "",
    )
    created = crud.create_item(certificate)
    pdf_bytes = make_certificate_pdf(created, student_name=(user.full_name or ""), school_name=school_name)
    cert_dir = Path("static/certificates")
    cert_dir.mkdir(parents=True, exist_ok=True)
    file_path = cert_dir / f"certificate_{created.id}.pdf"
    file_path.write_bytes(pdf_bytes)
    update_resource(models.Certificate, created.id, {"file_path": str(file_path)})
    created.file_path = str(file_path)
    return created


@router.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    certificate = get_resource(models.Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if not certificate.file_path or not Path(certificate.file_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found. Generate the certificate first.")
    return FileResponse(certificate.file_path, media_type="application/pdf", filename=f"certificate_{certificate.id}.pdf")


@router.get("/certificates/{certificate_id}/preview")
def preview_certificate(certificate_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    certificate = get_resource(models.Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if certificate.file_path and Path(certificate.file_path).exists():
        return FileResponse(certificate.file_path, media_type="application/pdf")
    student = get_resource(models.Student, certificate.student_id)
    with Session(engine) as session:
        user = session.get(models.User, student.user_id) if student else None
    school_name = "School ERP"
    settings = crud.get_item(models.SchoolSettings, 1)
    if settings and settings.school_name:
        school_name = settings.school_name
    pdf_bytes = make_certificate_pdf(certificate, student_name=(user.full_name or "") if user else "", school_name=school_name)
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")


# ========== SCHOOL SETTINGS ==========
@router.get("/settings", response_model=schemas.SchoolSettingsRead)
def get_settings(current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    with Session(engine) as session:
        sid = get_current_school_id()
        if sid is None:
            sid = current_user.school_id or 1
        statement = select(models.SchoolSettings).where(models.SchoolSettings.school_id == sid)
        settings = session.exec(statement).first()
        if not settings:
            settings = crud.create_item(models.SchoolSettings(school_name="My School", school_id=sid))
    return settings


@router.put("/settings", response_model=schemas.SchoolSettingsRead)
def update_settings(settings_update: schemas.SchoolSettingsUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    with Session(engine) as session:
        sid = get_current_school_id()
        if sid is None:
            sid = current_user.school_id or 1
        statement = select(models.SchoolSettings).where(models.SchoolSettings.school_id == sid)
        settings = session.exec(statement).first()
        if not settings:
            settings = crud.create_item(models.SchoolSettings(school_name="My School", school_id=sid))
        updated = update_resource(models.SchoolSettings, settings.id, settings_update.dict(exclude_unset=True))
    return updated


@router.post("/settings/logo", status_code=status.HTTP_200_OK)
async def upload_logo(file: UploadFile = File(...), current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return _upload_settings_file(file, "logo")


@router.post("/settings/stamp", status_code=status.HTTP_200_OK)
async def upload_stamp(file: UploadFile = File(...), current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return _upload_settings_file(file, "stamp")


@router.post("/settings/signature", status_code=status.HTTP_200_OK)
async def upload_signature(file: UploadFile = File(...), current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return _upload_settings_file(file, "signature")


def _upload_settings_file(file: UploadFile, field_name: str) -> dict:
    """Upload a settings asset (logo, stamp, signature) and update SchoolSettings."""
    sid = get_current_school_id()
    if sid is None:
        sid = 1
    upload_dir = Path("static/uploads")
    upload_dir = upload_dir / f"school_{sid}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    import time
    unique = int(time.time() * 1000)
    file_ext = Path(file.filename or "file").suffix or ".png"
    file_path = upload_dir / f"{field_name}_{unique}{file_ext}"
    contents = file.file.read()
    file_path.write_bytes(contents)
    with Session(engine) as session:
        statement = select(models.SchoolSettings).where(models.SchoolSettings.school_id == sid)
        settings = session.exec(statement).first()
        if not settings:
            settings = crud.create_item(models.SchoolSettings(school_name="My School", school_id=sid, **{f"{field_name}_path": str(file_path)}))
        else:
            update_resource(models.SchoolSettings, settings.id, {f"{field_name}_path": str(file_path)})
    return {f"{field_name}_path": str(file_path)}


# ========== NOTICE ENHANCEMENTS ==========
@router.get("/notices/filter", response_model=List[schemas.NoticeRead])
def filter_notices(
    target_role: Optional[str] = None,
    scheduled: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES)),
):
    with Session(engine) as session:
        statement = select(models.Notice)
        if target_role:
            statement = statement.where(
                or_(
                    models.Notice.target_roles == "all",
                    models.Notice.target_roles.contains(target_role),
                )
            )
        if scheduled is True:
            statement = statement.where(models.Notice.scheduled_for.isnot(None))
        elif scheduled is False:
            statement = statement.where(models.Notice.scheduled_for.is_(None))
        statement = statement.order_by(models.Notice.created_on.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()


@router.post("/notices/{notice_id}/attachments", status_code=status.HTTP_200_OK)
async def upload_notice_attachment(notice_id: int, file: UploadFile = File(...), current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    notice = get_resource(models.Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"notice_{notice_id}_{file.filename}"
    contents = await file.read()
    file_path.write_bytes(contents)
    update_resource(models.Notice, notice_id, {"attachments_path": str(file_path)})
    return {"attachments_path": str(file_path)}


# ========== STUDENT PORTAL ==========
@router.get("/portal/student/dashboard")
def student_portal_dashboard(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student.id)).first()
        cls_name = ""
        sec_name = ""
        ac_year = ""
        class_teacher = ""
        if enrollment:
            c = session.get(models.SchoolClass, enrollment.class_id)
            if c: cls_name = c.name
            s = session.get(models.Section, enrollment.section_id) if enrollment.section_id else None
            if s: sec_name = s.name
            ay = session.get(models.AcademicYear, enrollment.academic_year_id)
            if ay: ac_year = ay.name
            # Find class teacher from subject allocations
            alloc = session.exec(select(models.SubjectAllocation).where(models.SubjectAllocation.class_id == enrollment.class_id)).first()
            if alloc:
                t = session.get(models.Teacher, alloc.teacher_id)
                if t:
                    tu = session.get(models.User, t.user_id)
                    if tu: class_teacher = tu.full_name or ""
        total_att = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id)).one() or 0
        present_att = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id, models.Attendance.status == "present")).one() or 0
        att_pct = round((present_att / total_att * 100), 1) if total_att else 0
        pending_hw_count = 0
        if enrollment:
            all_hw = session.exec(select(models.Homework).where(models.Homework.class_id == enrollment.class_id)).all()
            submitted_ids = set(r.homework_id for r in session.exec(select(models.HomeworkSubmission).where(models.HomeworkSubmission.student_id == student.id)).all())
            pending_hw_count = len([h for h in all_hw if h.id not in submitted_ids])
        upcoming_exams = session.exec(select(func.count(models.Exam.id)).where(models.Exam.start_date >= date.today())).one() or 0
        pending_fees = session.exec(select(func.count(models.FeeAssignment.id)).where(models.FeeAssignment.student_id == student.id, models.FeeAssignment.is_paid == False)).one() or 0
        notices = session.exec(select(models.Notice).where(
            or_(models.Notice.target_roles == "all", models.Notice.target_roles.contains("Student"), models.Notice.target_roles.is_(None))
        ).order_by(models.Notice.created_on.desc()).limit(5)).all()
        events = session.exec(select(models.Event).where(models.Event.start_date >= datetime.utcnow()).order_by(models.Event.start_date).limit(5)).all()
        unread_msgs = session.exec(select(func.count(models.Message.id)).where(models.Message.recipient_id == current_user.id, models.Message.is_read == False)).one() or 0
        # Monthly attendance for chart
        monthly_att = []
        for m in range(1, 13):
            cnt = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id, func.extract('month', models.Attendance.date) == m, models.Attendance.status == "present")).one() or 0
            tot = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id, func.extract('month', models.Attendance.date) == m)).one() or 0
            monthly_att.append({"month": m, "present": cnt, "total": tot})
        # Exam performance
        exam_results = session.exec(select(models.ExamResult, models.Exam).join(models.Exam, models.ExamResult.exam_id == models.Exam.id).where(models.ExamResult.student_id == student.id)).all()
        exam_perf = {}
        for r, e in exam_results:
            if e.name not in exam_perf:
                exam_perf[e.name] = {"total": 0, "obtained": 0, "count": 0}
            exam_perf[e.name]["total"] += (r.max_marks or 0)
            exam_perf[e.name]["obtained"] += (r.marks_obtained or 0)
            exam_perf[e.name]["count"] += 1
        exam_data = [{"name": k, "percentage": round((v["obtained"]/v["total"]*100), 1) if v["total"] else 0} for k, v in exam_perf.items()]
        return {
            "student": {"id": student.id, "admission_no": student.admission_no, "roll_no": student.admission_no, "full_name": current_user.full_name, "email": current_user.email, "photo_path": student.photo_path},
            "class_name": cls_name, "section_name": sec_name, "academic_year": ac_year, "class_teacher": class_teacher,
            "attendance_percentage": att_pct, "pending_homework": pending_hw_count,
            "upcoming_exams": upcoming_exams, "fee_balance": pending_fees,
            "notices": notices, "events": events, "unread_messages": unread_msgs,
            "monthly_attendance": monthly_att, "exam_performance": exam_data,
        }


@router.get("/portal/student/profile")
def student_portal_profile(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student.id)).first()
        cls_name, sec_name = "", ""
        if enrollment:
            c = session.get(models.SchoolClass, enrollment.class_id)
            if c: cls_name = c.name
            s = session.get(models.Section, enrollment.section_id) if enrollment.section_id else None
            if s: sec_name = s.name
        return {
            "id": student.id, "user_id": student.user_id, "admission_no": student.admission_no,
            "full_name": current_user.full_name, "email": current_user.email,
            "dob": student.dob, "gender": student.gender, "admission_date": student.admission_date,
            "status": student.status, "photo_path": student.photo_path,
            "class_name": cls_name, "section_name": sec_name,
            "phone": current_user.full_name, "address": "",
        }


@router.put("/portal/student/profile")
def student_update_profile(profile_update: dict, current_user=Depends(auth.require_roles("Student"))):
    """Update editable fields: full_name, photo_path. Cannot change admission_no, class, section."""
    allowed = {"full_name": str}
    updates = {k: v for k, v in profile_update.items() if k in allowed}
    user = crud.update_user(current_user.id, updates)
    if not user:
        raise HTTPException(404, "User not found")
    return {"msg": "Profile updated"}


@router.post("/portal/student/change-password")
def student_change_password(data: schemas.PasswordChange, current_user=Depends(auth.require_roles("Student"))):
    if not auth.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    hashed = auth.get_password_hash(data.new_password)
    crud.update_user(current_user.id, {"hashed_password": hashed})
    return {"msg": "Password changed successfully"}


@router.post("/portal/student/photo")
async def student_upload_photo(file: UploadFile = File(...), current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student not found")
        upload_dir = Path("static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"student_portal_photo_{student.id}_{file.filename}"
        contents = await file.read()
        file_path.write_bytes(contents)
        update_resource(models.Student, student.id, {"photo_path": str(file_path)})
        return {"photo_path": str(file_path)}


@router.get("/portal/student/attendance")
def student_portal_attendance(
    month: Optional[int] = None,
    year: Optional[int] = None,
    subject_id: Optional[int] = None,
    current_user=Depends(auth.require_roles("Student"))
):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        query = select(models.Attendance).where(models.Attendance.student_id == student.id)
        if month:
            query = query.where(func.extract('month', models.Attendance.date) == month)
        if year:
            query = query.where(func.extract('year', models.Attendance.date) == year)
        records = session.exec(query.order_by(models.Attendance.date.desc()).limit(365)).all()
        monthly = []
        for m in range(1, 13):
            cnt = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id, func.extract('month', models.Attendance.date) == m, models.Attendance.status == "present")).one() or 0
            total = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id, func.extract('month', models.Attendance.date) == m)).one() or 0
            monthly.append({"month": m, "present": cnt, "total": total})
        total = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id)).one() or 0
        present = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student.id, models.Attendance.status == "present")).one() or 0
        pct = round((present / total * 100), 1) if total else 0
        # Subject-wise attendance
        subject_attendance = {}
        if subject_id:
            pass
        return {"records": records, "monthly": monthly, "percentage": pct, "total": total, "present": present, "absent": total - present}


@router.get("/portal/student/attendance/download")
def student_attendance_download(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student not found")
        records = session.exec(select(models.Attendance).where(models.Attendance.student_id == student.id).order_by(models.Attendance.date.desc())).all()
        headers = ["Date", "Status", "Remarks"]
        rows = [[str(r.date), r.status, r.remarks or ""] for r in records]
        return make_csv_response(f"attendance_{student.admission_no}.csv", headers, rows)


@router.get("/portal/student/homework")
def student_portal_homework(
    skip: int = 0, limit: int = 50,
    subject_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user=Depends(auth.require_roles("Student"))
):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student.id)).first()
        if not enrollment:
            return {"homework": [], "total": 0}
        hw_query = select(models.Homework).where(models.Homework.class_id == enrollment.class_id)
        if subject_id:
            hw_query = hw_query.where(models.Homework.id.in_(
                select(models.SubjectAllocation.subject_id).where(models.SubjectAllocation.class_id == enrollment.class_id)
            ))
        total_hw = session.exec(select(func.count()).select_from(hw_query.subquery())).one() if False else 0
        homeworks = session.exec(hw_query.order_by(models.Homework.due_date.desc()).offset(skip).limit(limit)).all()
        submissions = session.exec(select(models.HomeworkSubmission).where(models.HomeworkSubmission.student_id == student.id)).all()
        sub_map = {s.homework_id: s for s in submissions}
        result = []
        for hw in homeworks:
            sub = sub_map.get(hw.id)
            status = "pending"
            if sub:
                if sub.status == "graded":
                    status = "graded"
                elif sub.status == "submitted":
                    status = "submitted"
                elif hw.due_date and hw.due_date < date.today():
                    status = "late"
            if status_filter and status != status_filter:
                continue
            result.append({
                "homework": hw, "submission": sub, "status": status,
            })
        return {"homework": result, "total": len(homeworks)}


@router.post("/portal/student/homework/{homework_id}/submit")
async def student_submit_homework(
    homework_id: int,
    file: Optional[UploadFile] = None,
    remarks: Optional[str] = None,
    current_user=Depends(auth.require_roles("Student"))
):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student not found")
        hw = session.get(models.Homework, homework_id)
        if not hw:
            raise HTTPException(404, "Homework not found")
        # Check existing submission
        existing = session.exec(select(models.HomeworkSubmission).where(
            models.HomeworkSubmission.homework_id == homework_id,
            models.HomeworkSubmission.student_id == student.id
        )).first()
        if existing and hw.due_date and hw.due_date < date.today():
            raise HTTPException(400, "Cannot replace submission after due date")
        attachment_path = None
        if file:
            upload_dir = Path("static/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / f"hw_sub_{student.id}_{homework_id}_{file.filename}"
            contents = await file.read()
            file_path.write_bytes(contents)
            attachment_path = str(file_path)
        if existing:
            existing.attachment_path = attachment_path or existing.attachment_path
            existing.remarks = remarks or existing.remarks
            existing.submitted_on = datetime.utcnow()
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing
        else:
            sub = models.HomeworkSubmission(
                homework_id=homework_id, student_id=student.id,
                attachment_path=attachment_path, remarks=remarks, status="submitted",
                school_id=current_user.school_id,
            )
            session.add(sub)
            session.commit()
            session.refresh(sub)
            return sub


@router.get("/portal/student/exams")
def student_portal_exams(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        upcoming = session.exec(select(models.Exam).where(models.Exam.start_date >= date.today()).order_by(models.Exam.start_date).limit(20)).all()
        results = session.exec(select(models.ExamResult, models.Subject, models.Exam)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .join(models.Exam, models.ExamResult.exam_id == models.Exam.id)
            .where(models.ExamResult.student_id == student.id)).all()
        result_list = []
        total_obtained = 0
        total_max = 0
        for r, sub, e in results:
            result_list.append({"result": r, "subject_name": sub.name, "exam_name": e.name})
            total_obtained += (r.marks_obtained or 0)
            total_max += (r.max_marks or 0)
        percentage = round((total_obtained / total_max * 100), 2) if total_max else 0
        gpa = round((percentage / 100) * 4.0, 2) if percentage else 0
        # Class rank
        rank = 0
        if results:
            first_result = results[0]
            all_scores = session.exec(
                select(func.sum(models.ExamResult.marks_obtained)).where(
                    models.ExamResult.exam_id == first_result.Exam.id
                ).group_by(models.ExamResult.student_id)
            ).all()
            sorted_scores = sorted([float(s or 0) for s in all_scores], reverse=True)
            rank = sorted_scores.index(total_obtained) + 1 if total_obtained in sorted_scores else 0
        return {
            "upcoming_exams": upcoming, "results": result_list,
            "total_obtained": total_obtained, "total_max": total_max,
            "percentage": percentage, "gpa": gpa, "rank": rank,
        }


@router.get("/portal/student/exams/report-card")
def student_report_card(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student not found")
        user = session.get(models.User, student.user_id)
        results = session.exec(select(models.ExamResult, models.Subject, models.Exam)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .join(models.Exam, models.ExamResult.exam_id == models.Exam.id)
            .where(models.ExamResult.student_id == student.id)).all()
        school_name = "School ERP"
        settings = crud.get_item(models.SchoolSettings, 1)
        if settings and settings.school_name:
            school_name = settings.school_name
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)
        pdf.cell(0, 12, school_name, ln=True, align='C')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Report Card', ln=True, align='C')
        pdf.ln(5)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Student: {user.full_name or student.admission_no}', ln=True)
        pdf.cell(0, 8, f'Admission No: {student.admission_no or ""}', ln=True)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(60, 8, 'Subject', 1)
        pdf.cell(30, 8, 'Marks', 1)
        pdf.cell(30, 8, 'Max', 1)
        pdf.cell(30, 8, 'Exam', 1)
        pdf.ln()
        pdf.set_font('Arial', '', 11)
        for r, sub, e in results:
            pdf.cell(60, 8, sub.name, 1)
            pdf.cell(30, 8, str(r.marks_obtained or ''), 1)
            pdf.cell(30, 8, str(r.max_marks or ''), 1)
            pdf.cell(30, 8, e.name, 1)
            pdf.ln()
        pdf_bytes = bytes(pdf.output(dest='S'))
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename="report_card.pdf"'})


@router.get("/portal/student/fees")
def student_portal_fees(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        assignments = session.exec(
            select(models.FeeAssignment, models.FeeStructure)
            .join(models.FeeStructure, models.FeeAssignment.fee_structure_id == models.FeeStructure.id)
            .where(models.FeeAssignment.student_id == student.id)
        ).all()
        assignment_ids = [a.id for a, _ in assignments]
        payments = []
        if assignment_ids:
            payments = session.exec(
                select(models.Payment).where(models.Payment.fee_assignment_id.in_(assignment_ids))
            ).all()
        pending = [{"assignment": a, "structure": s} for a, s in assignments if not a.is_paid]
        paid = [{"assignment": a, "structure": s} for a, s in assignments if a.is_paid]
        return {"assignments": [{"assignment": a, "structure": s} for a, s in assignments], "payments": payments, "pending": pending, "paid": paid}


@router.get("/portal/student/fees/receipt/{payment_id}")
def student_fee_receipt(payment_id: int, current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        payment = session.get(models.Payment, payment_id)
        if not payment:
            raise HTTPException(404, "Payment not found")
        assignment = session.get(models.FeeAssignment, payment.fee_assignment_id)
        if not assignment:
            raise HTTPException(404, "Fee assignment not found")
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if assignment.student_id != student.id:
            raise HTTPException(403, "Not authorized")
        school_name = "School ERP"
        settings = crud.get_item(models.SchoolSettings, 1)
        if settings and settings.school_name:
            school_name = settings.school_name
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 12, school_name, ln=True, align='C')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Fee Receipt', ln=True, align='C')
        pdf.ln(5)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Receipt No: {payment.id}', ln=True)
        pdf.cell(0, 8, f'Amount: ${payment.amount}', ln=True)
        pdf.cell(0, 8, f'Date: {payment.paid_on.strftime("%d %B %Y")}', ln=True)
        pdf.cell(0, 8, f'Reference: {payment.reference or "N/A"}', ln=True)
        pdf_bytes = bytes(pdf.output(dest='S'))
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="receipt_{payment.id}.pdf"'})


@router.get("/portal/student/notices")
def student_portal_notices(
    skip: int = 0, limit: int = 20,
    search: Optional[str] = None,
    current_user=Depends(auth.require_roles("Student"))
):
    with Session(engine) as session:
        query = select(models.Notice).where(
            or_(models.Notice.target_roles == "all", models.Notice.target_roles.contains("Student"), models.Notice.target_roles.is_(None))
        )
        if search:
            query = query.where(models.Notice.title.contains(search))
        total = session.exec(select(func.count()).select_from(query.subquery())).one() if False else 0
        notices = session.exec(query.order_by(models.Notice.created_on.desc()).offset(skip).limit(limit)).all()
        return {"notices": notices, "total": len(notices)}


@router.get("/portal/student/calendar")
def student_portal_calendar(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        events = session.exec(select(models.Event).where(models.Event.start_date >= datetime.utcnow()).order_by(models.Event.start_date).limit(50)).all()
        exams = session.exec(select(models.Exam).where(models.Exam.start_date >= date.today()).order_by(models.Exam.start_date).limit(50)).all()
        if student:
            enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student.id)).first()
            if enrollment:
                homeworks = session.exec(select(models.Homework).where(
                    models.Homework.class_id == enrollment.class_id,
                    models.Homework.due_date >= date.today()
                ).order_by(models.Homework.due_date).limit(50)).all()
            else:
                homeworks = []
        else:
            homeworks = []
        return {"events": events, "exams": exams, "homeworks": homeworks}


@router.get("/portal/student/documents")
def student_portal_documents(current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        student = session.exec(select(models.Student).where(models.Student.user_id == current_user.id)).first()
        if not student:
            raise HTTPException(404, "Student profile not found")
        docs = session.exec(select(models.Document).where(models.Document.owner_type == "student", models.Document.owner_id == student.id)).all()
        certs = session.exec(select(models.Certificate).where(models.Certificate.student_id == student.id)).all()
        # Fee receipts
        assignments = session.exec(select(models.FeeAssignment).where(models.FeeAssignment.student_id == student.id)).all()
        assignment_ids = [a.id for a in assignments]
        payments = []
        if assignment_ids:
            payments = session.exec(select(models.Payment).where(models.Payment.fee_assignment_id.in_(assignment_ids))).all()
        return {"documents": docs, "certificates": certs, "payments": payments}


@router.get("/portal/student/messages")
def student_portal_messages(skip: int = 0, limit: int = 50, search: Optional[str] = None, current_user=Depends(auth.require_roles("Student"))):
    with Session(engine) as session:
        query = select(models.Message).where(
            or_(models.Message.recipient_id == current_user.id, models.Message.sender_id == current_user.id)
        )
        if search:
            query = query.where(models.Message.subject.contains(search))
        messages = session.exec(query.order_by(models.Message.sent_on.desc()).offset(skip).limit(limit)).all()
        unread = session.exec(select(func.count(models.Message.id)).where(models.Message.recipient_id == current_user.id, models.Message.is_read == False)).one() or 0
        return {"messages": messages, "unread": unread}


@router.post("/portal/student/messages")
def student_send_message(msg_in: schemas.MessageCreate, current_user=Depends(auth.require_roles("Student"))):
    msg_in.sender_id = current_user.id
    return create_resource(msg_in, models.Message, current_user)


@router.put("/portal/student/messages/{message_id}/read")
def student_mark_read(message_id: int, current_user=Depends(auth.require_roles("Student"))):
    msg = update_resource(models.Message, message_id, {"is_read": True})
    if not msg:
        raise HTTPException(404)
    return msg


# ========== PARENT PORTAL ==========
@router.get("/portal/parent/profile")
def parent_portal_profile(current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        parent = session.exec(select(models.Parent).where(models.Parent.user_id == current_user.id)).first()
        if not parent:
            raise HTTPException(404, "Parent profile not found")
        return {
            "id": parent.id, "user_id": parent.user_id,
            "full_name": current_user.full_name, "email": current_user.email,
            "phone": parent.phone or "", "address": parent.address or "",
        }


@router.put("/portal/parent/profile")
def parent_update_profile(profile_update: dict, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        parent = session.exec(select(models.Parent).where(models.Parent.user_id == current_user.id)).first()
        if not parent:
            raise HTTPException(404, "Parent not found")
        if "phone" in profile_update:
            update_resource(models.Parent, parent.id, {"phone": profile_update["phone"]})
        if "address" in profile_update:
            update_resource(models.Parent, parent.id, {"address": profile_update["address"]})
        if "full_name" in profile_update:
            crud.update_user(current_user.id, {"full_name": profile_update["full_name"]})
        return {"msg": "Profile updated"}


@router.post("/portal/parent/change-password")
def parent_change_password(data: schemas.PasswordChange, current_user=Depends(auth.require_roles("Parent"))):
    if not auth.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    hashed = auth.get_password_hash(data.new_password)
    crud.update_user(current_user.id, {"hashed_password": hashed})
    return {"msg": "Password changed successfully"}


@router.get("/portal/parent/dashboard")
def parent_portal_dashboard(current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        parent = session.exec(select(models.Parent).where(models.Parent.user_id == current_user.id)).first()
        if not parent:
            raise HTTPException(404, "Parent profile not found")
        children = session.exec(select(models.Student).where(or_(models.Student.father_id == parent.id, models.Student.mother_id == parent.id))).all()
        result = []
        total_pending_fees = 0
        for child in children:
            total_att = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == child.id)).one() or 0
            present_att = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == child.id, models.Attendance.status == "present")).one() or 0
            pending_fees = session.exec(select(func.count(models.FeeAssignment.id)).where(models.FeeAssignment.student_id == child.id, models.FeeAssignment.is_paid == False)).one() or 0
            total_pending_fees += pending_fees
            enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == child.id)).first()
            cls_name = ""
            if enrollment:
                c = session.get(models.SchoolClass, enrollment.class_id)
                if c: cls_name = c.name
            user = session.get(models.User, child.user_id)
            result.append({
                "student_id": child.id, "admission_no": child.admission_no,
                "full_name": user.full_name if user else "",
                "class_name": cls_name,
                "attendance_pct": round((present_att / total_att * 100), 1) if total_att else 0,
                "pending_fees": pending_fees,
            })
        notices = session.exec(select(models.Notice).where(
            or_(models.Notice.target_roles == "all", models.Notice.target_roles.contains("Parent"), models.Notice.target_roles.is_(None))
        ).order_by(models.Notice.created_on.desc()).limit(5)).all()
        upcoming_exams = session.exec(select(func.count(models.Exam.id)).where(models.Exam.start_date >= date.today())).one() or 0
        pending_hw = 0
        for child in children:
            enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == child.id)).first()
            if enrollment:
                all_hw = session.exec(select(models.Homework).where(models.Homework.class_id == enrollment.class_id)).all()
                submitted_ids = set(r.homework_id for r in session.exec(select(models.HomeworkSubmission).where(models.HomeworkSubmission.student_id == child.id)).all())
                pending_hw += len([h for h in all_hw if h.id not in submitted_ids])
        return {
            "children": result, "notices": notices, "total_children": len(children),
            "total_pending_fees": total_pending_fees, "upcoming_exams": upcoming_exams,
            "pending_homework": pending_hw,
        }


@router.get("/portal/parent/children")
def parent_portal_children(current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        parent = session.exec(select(models.Parent).where(models.Parent.user_id == current_user.id)).first()
        if not parent:
            raise HTTPException(404, "Parent not found")
        children = session.exec(select(models.Student).where(or_(models.Student.father_id == parent.id, models.Student.mother_id == parent.id))).all()
        result = []
        for child in children:
            user = session.get(models.User, child.user_id)
            enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == child.id)).first()
            cls_name, sec_name = "", ""
            if enrollment:
                c = session.get(models.SchoolClass, enrollment.class_id)
                if c: cls_name = c.name
                s = session.get(models.Section, enrollment.section_id) if enrollment.section_id else None
                if s: sec_name = s.name
            result.append({
                "student_id": child.id, "admission_no": child.admission_no,
                "full_name": user.full_name if user else "",
                "class_name": cls_name, "section_name": sec_name,
                "photo_path": child.photo_path, "dob": child.dob, "gender": child.gender,
            })
        return {"children": result}


@router.get("/portal/parent/children/{student_id}/profile")
def parent_portal_child_profile(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        user = session.get(models.User, child.user_id)
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student_id)).first()
        cls_name, sec_name, ac_year = "", "", ""
        class_teacher_name = ""
        if enrollment:
            c = session.get(models.SchoolClass, enrollment.class_id)
            if c: cls_name = c.name
            s = session.get(models.Section, enrollment.section_id) if enrollment.section_id else None
            if s: sec_name = s.name
            ay = session.get(models.AcademicYear, enrollment.academic_year_id)
            if ay: ac_year = ay.name
            alloc = session.exec(select(models.SubjectAllocation).where(models.SubjectAllocation.class_id == enrollment.class_id)).first()
            if alloc:
                t = session.get(models.Teacher, alloc.teacher_id)
                if t:
                    tu = session.get(models.User, t.user_id)
                    if tu: class_teacher_name = tu.full_name or ""
        return {
            "id": child.id, "admission_no": child.admission_no,
            "full_name": user.full_name if user else "", "email": user.email if user else "",
            "dob": child.dob, "gender": child.gender, "photo_path": child.photo_path,
            "class_name": cls_name, "section_name": sec_name, "academic_year": ac_year,
            "class_teacher": class_teacher_name,
        }


@router.get("/portal/parent/children/{student_id}/attendance")
def parent_portal_child_attendance(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        records = session.exec(select(models.Attendance).where(models.Attendance.student_id == student_id).order_by(models.Attendance.date.desc()).limit(200)).all()
        monthly = []
        for m in range(1, 13):
            cnt = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student_id, func.extract('month', models.Attendance.date) == m, models.Attendance.status == "present")).one() or 0
            total = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student_id, func.extract('month', models.Attendance.date) == m)).one() or 0
            monthly.append({"month": m, "present": cnt, "total": total})
        total = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student_id)).one() or 0
        present = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student_id, models.Attendance.status == "present")).one() or 0
        pct = round((present / total * 100), 1) if total else 0
        return {"records": records, "monthly": monthly, "percentage": pct, "total": total, "present": present}


@router.get("/portal/parent/children/{student_id}/attendance/download")
def parent_child_attendance_download(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        records = session.exec(select(models.Attendance).where(models.Attendance.student_id == student_id).order_by(models.Attendance.date.desc())).all()
        headers = ["Date", "Status", "Remarks"]
        rows = [[str(r.date), r.status, r.remarks or ""] for r in records]
        return make_csv_response(f"attendance_{child.admission_no}.csv", headers, rows)


@router.get("/portal/parent/children/{student_id}/homework")
def parent_portal_child_homework(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student_id)).first()
        if not enrollment:
            return {"homework": []}
        homeworks = session.exec(select(models.Homework).where(models.Homework.class_id == enrollment.class_id).order_by(models.Homework.due_date.desc()).limit(50)).all()
        submissions = session.exec(select(models.HomeworkSubmission).where(models.HomeworkSubmission.student_id == student_id)).all()
        sub_map = {s.homework_id: s for s in submissions}
        result = []
        for hw in homeworks:
            sub = sub_map.get(hw.id)
            result.append({"homework": hw, "submission": sub, "status": sub.status if sub else "pending"})
        return {"homework": result}


@router.get("/portal/parent/children/{student_id}/results")
def parent_portal_child_results(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        results = session.exec(select(models.ExamResult, models.Subject, models.Exam)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .join(models.Exam, models.ExamResult.exam_id == models.Exam.id)
            .where(models.ExamResult.student_id == student_id)).all()
        total_obtained = sum(r.marks_obtained or 0 for r, _, _ in results)
        total_max = sum(r.max_marks or 0 for r, _, _ in results)
        percentage = round((total_obtained / total_max * 100), 2) if total_max else 0
        gpa = round((percentage / 100) * 4.0, 2) if percentage else 0
        return {"results": [{"result": r, "subject": s, "exam": e} for r, s, e in results],
                "total_obtained": total_obtained, "total_max": total_max,
                "percentage": percentage, "gpa": gpa}


@router.get("/portal/parent/children/{student_id}/results/report-card")
def parent_child_report_card(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        user = session.get(models.User, child.user_id)
        results = session.exec(select(models.ExamResult, models.Subject, models.Exam)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .join(models.Exam, models.ExamResult.exam_id == models.Exam.id)
            .where(models.ExamResult.student_id == student_id)).all()
        school_name = "School ERP"
        settings = crud.get_item(models.SchoolSettings, 1)
        if settings and settings.school_name: school_name = settings.school_name
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)
        pdf.cell(0, 12, school_name, ln=True, align='C')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Report Card', ln=True, align='C')
        pdf.ln(5)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Student: {user.full_name or child.admission_no}', ln=True)
        pdf.cell(0, 8, f'Admission No: {child.admission_no or ""}', ln=True)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(60, 8, 'Subject', 1)
        pdf.cell(30, 8, 'Marks', 1)
        pdf.cell(30, 8, 'Max', 1)
        pdf.cell(30, 8, 'Exam', 1)
        pdf.ln()
        pdf.set_font('Arial', '', 11)
        for r, sub, e in results:
            pdf.cell(60, 8, sub.name, 1)
            pdf.cell(30, 8, str(r.marks_obtained or ''), 1)
            pdf.cell(30, 8, str(r.max_marks or ''), 1)
            pdf.cell(30, 8, e.name, 1)
            pdf.ln()
        pdf_bytes = bytes(pdf.output(dest='S'))
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename="report_card.pdf"'})


@router.get("/portal/parent/children/{student_id}/fees")
def parent_portal_child_fees(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        assignments = session.exec(select(models.FeeAssignment, models.FeeStructure)
            .join(models.FeeStructure, models.FeeAssignment.fee_structure_id == models.FeeStructure.id)
            .where(models.FeeAssignment.student_id == student_id)).all()
        assignment_ids = [a.id for a, _ in assignments]
        payments = []
        if assignment_ids:
            payments = session.exec(select(models.Payment).where(models.Payment.fee_assignment_id.in_(assignment_ids))).all()
        total_due = sum(s.amount for a, s in assignments if not a.is_paid)
        return {"assignments": [{"assignment": a, "structure": s} for a, s in assignments],
                "payments": payments, "total_due": total_due}


@router.get("/portal/parent/notices")
def parent_portal_notices(skip: int = 0, limit: int = 20, search: Optional[str] = None, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        query = select(models.Notice).where(
            or_(models.Notice.target_roles == "all", models.Notice.target_roles.contains("Parent"), models.Notice.target_roles.is_(None))
        )
        if search:
            query = query.where(models.Notice.title.contains(search))
        notices = session.exec(query.order_by(models.Notice.created_on.desc()).offset(skip).limit(limit)).all()
        return {"notices": notices, "total": len(notices)}


@router.get("/portal/parent/calendar")
def parent_portal_calendar(current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        events = session.exec(select(models.Event).where(models.Event.start_date >= datetime.utcnow()).order_by(models.Event.start_date).limit(50)).all()
        exams = session.exec(select(models.Exam).where(models.Exam.start_date >= date.today()).order_by(models.Exam.start_date).limit(50)).all()
        return {"events": events, "exams": exams}


@router.get("/portal/parent/messages")
def parent_portal_messages(skip: int = 0, limit: int = 50, search: Optional[str] = None, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        query = select(models.Message).where(
            or_(models.Message.recipient_id == current_user.id, models.Message.sender_id == current_user.id)
        )
        if search:
            query = query.where(models.Message.subject.contains(search))
        messages = session.exec(query.order_by(models.Message.sent_on.desc()).offset(skip).limit(limit)).all()
        unread = session.exec(select(func.count(models.Message.id)).where(models.Message.recipient_id == current_user.id, models.Message.is_read == False)).one() or 0
        return {"messages": messages, "unread": unread}


@router.post("/portal/parent/messages")
def parent_send_message(msg_in: schemas.MessageCreate, current_user=Depends(auth.require_roles("Parent"))):
    msg_in.sender_id = current_user.id
    return create_resource(msg_in, models.Message, current_user)


@router.get("/portal/parent/children/{student_id}/certificates")
def parent_portal_child_certificates(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        verify_child_ownership(student_id, current_user)
        certificates = session.exec(select(models.Certificate).where(models.Certificate.student_id == student_id).order_by(models.Certificate.issue_date.desc())).all()
        return {"certificates": certificates}


@router.get("/portal/parent/children/{student_id}/certificates/{cert_id}/download")
def parent_child_certificate_download(student_id: int, cert_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        cert = session.get(models.Certificate, cert_id)
        if not cert or cert.student_id != student_id:
            raise HTTPException(404, "Certificate not found")
        user = session.get(models.User, child.user_id)
        school_name = "School ERP"
        settings = crud.get_item(models.SchoolSettings, 1)
        if settings and settings.school_name: school_name = settings.school_name
        pdf_bytes = make_certificate_pdf(cert, user.full_name if user else "", school_name)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="certificate_{cert_id}.pdf"'})


@router.get("/portal/parent/children/{student_id}/documents")
def parent_portal_child_documents(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        documents = session.exec(select(models.Document).where(
            models.Document.owner_type == "student",
            models.Document.owner_id == student_id
        ).order_by(models.Document.uploaded_on.desc())).all()
        return {"documents": documents}


@router.get("/portal/parent/children/{student_id}/progress")
def parent_portal_child_progress(student_id: int, current_user=Depends(auth.require_roles("Parent"))):
    with Session(engine) as session:
        child = verify_child_ownership(student_id, current_user)
        # Attendance trend
        monthly_att = []
        for m in range(1, 13):
            cnt = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student_id, func.extract('month', models.Attendance.date) == m, models.Attendance.status == "present")).one() or 0
            total = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.student_id == student_id, func.extract('month', models.Attendance.date) == m)).one() or 0
            monthly_att.append({"month": m, "present": cnt, "total": total, "pct": round((cnt/total*100), 1) if total else 0})
        # Academic trend
        results = session.exec(select(models.ExamResult, models.Subject, models.Exam)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .join(models.Exam, models.ExamResult.exam_id == models.Exam.id)
            .where(models.ExamResult.student_id == student_id)).all()
        exam_data = {}
        for r, sub, e in results:
            if e.name not in exam_data:
                exam_data[e.name] = {"total": 0, "obtained": 0}
            exam_data[e.name]["total"] += (r.max_marks or 0)
            exam_data[e.name]["obtained"] += (r.marks_obtained or 0)
        academic_trend = [{"name": k, "pct": round((v["obtained"]/v["total"]*100), 1) if v["total"] else 0} for k, v in exam_data.items()]
        # Homework completion
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student_id)).first()
        hw_completion = {"completed": 0, "pending": 0, "late": 0}
        if enrollment:
            all_hw = session.exec(select(models.Homework).where(models.Homework.class_id == enrollment.class_id)).all()
            submissions = session.exec(select(models.HomeworkSubmission).where(models.HomeworkSubmission.student_id == student_id)).all()
            sub_ids = {s.homework_id: s for s in submissions}
            for hw in all_hw:
                if hw.id in sub_ids:
                    sub = sub_ids[hw.id]
                    if sub.status == "graded":
                        hw_completion["completed"] += 1
                    else:
                        hw_completion["completed"] += 1
                else:
                    if hw.due_date and hw.due_date < date.today():
                        hw_completion["late"] += 1
                    else:
                        hw_completion["pending"] += 1
        # Subject performance
        subject_perf = {}
        for r, sub, e in results:
            if sub.name not in subject_perf:
                subject_perf[sub.name] = {"total": 0, "obtained": 0, "count": 0}
            subject_perf[sub.name]["total"] += (r.max_marks or 0)
            subject_perf[sub.name]["obtained"] += (r.marks_obtained or 0)
            subject_perf[sub.name]["count"] += 1
        subject_performance = [{"name": k, "pct": round((v["obtained"]/v["total"]*100), 1) if v["total"] else 0} for k, v in subject_perf.items()]
        return {
            "attendance_trend": monthly_att,
            "academic_trend": academic_trend,
            "homework_completion": hw_completion,
            "subject_performance": subject_performance,
        }


# ========== TEACHER PORTAL ==========
@router.get("/portal/teacher/dashboard")
def teacher_portal_dashboard(current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher profile not found")
        allocations = session.exec(select(models.SubjectAllocation).where(models.SubjectAllocation.teacher_id == teacher.id)).all()
        class_ids = list(set(a.class_id for a in allocations))
        classes = [session.get(models.SchoolClass, cid) for cid in class_ids if session.get(models.SchoolClass, cid)]
        total_students = 0
        for cid in class_ids:
            total_students += session.exec(select(func.count(models.Enrollment.id)).where(models.Enrollment.class_id == cid)).one() or 0
        today_att = session.exec(select(func.count(models.Attendance.id)).where(models.Attendance.date == date.today())).one() or 0
        pending_hw = session.exec(select(func.count(models.Homework.id)).where(models.Homework.assigned_by == teacher.id, models.Homework.due_date >= date.today())).one() or 0
        upcoming_exams = session.exec(select(func.count(models.Exam.id)).where(models.Exam.start_date >= date.today())).one() or 0
        unread_msgs = session.exec(select(func.count(models.Message.id)).where(models.Message.recipient_id == current_user.id, models.Message.is_read == False)).one() or 0
        return {
            "teacher": {"id": teacher.id, "employee_no": teacher.employee_no, "full_name": current_user.full_name},
            "assigned_classes": [{"id": c.id, "name": c.name} for c in classes if c],
            "total_students": total_students,
            "today_attendance": today_att,
            "pending_homework": pending_hw,
            "upcoming_exams": upcoming_exams,
            "unread_messages": unread_msgs,
        }


@router.get("/portal/teacher/classes")
def teacher_portal_classes(current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher profile not found")
        allocations = session.exec(select(models.SubjectAllocation, models.Subject, models.SchoolClass, models.Section)
            .join(models.Subject, models.SubjectAllocation.subject_id == models.Subject.id)
            .join(models.SchoolClass, models.SubjectAllocation.class_id == models.SchoolClass.id)
            .outerjoin(models.Section, models.SubjectAllocation.section_id == models.Section.id)
            .where(models.SubjectAllocation.teacher_id == teacher.id)).all()
        result = []
        for a, sub, cls, sec in allocations:
            student_count = session.exec(select(func.count(models.Enrollment.id)).where(models.Enrollment.class_id == a.class_id)).one() or 0
            result.append({"allocation": a, "subject": sub, "class": cls, "section": sec, "student_count": student_count})
        return result


@router.get("/portal/teacher/students")
def teacher_portal_students(class_id: Optional[int] = None, search: Optional[str] = None, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        allocations = session.exec(select(models.SubjectAllocation).where(models.SubjectAllocation.teacher_id == teacher.id)).all()
        class_ids = [a.class_id for a in allocations]
        if not class_ids:
            return []
        query = select(models.Student).where(models.Student.school_id == current_user.school_id, models.Student.id.in_(
            select(models.Enrollment.student_id).where(models.Enrollment.class_id.in_(class_ids))
        ))
        if class_id:
            query = query.where(models.Student.id.in_(
                select(models.Enrollment.student_id).where(models.Enrollment.class_id == class_id)
            ))
        students = session.exec(query).all()
        result = []
        for st in students:
            user = session.get(models.User, st.user_id)
            result.append({"student": st, "user": user})
        return result


@router.get("/portal/teacher/notices")
def teacher_portal_notices(skip: int = 0, limit: int = 50, search: Optional[str] = None, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        query = select(models.Notice).where(models.Notice.school_id == current_user.school_id)
        if search:
            query = query.where(models.Notice.title.contains(search))
        notices = session.exec(query.order_by(models.Notice.created_on.desc()).offset(skip).limit(limit)).all()
        return notices


@router.get("/portal/teacher/classes/{class_id}/students")
def teacher_class_students(class_id: int, search: Optional[str] = None, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        # Verify teacher is assigned to this class
        alloc = session.exec(select(models.SubjectAllocation).where(
            models.SubjectAllocation.teacher_id == teacher.id,
            models.SubjectAllocation.class_id == class_id
        )).first()
        if not alloc:
            raise HTTPException(403, "Not assigned to this class")
        enrollments = session.exec(select(models.Enrollment).where(models.Enrollment.class_id == class_id)).all()
        student_ids = [e.student_id for e in enrollments]
        students = []
        for sid in student_ids:
            s = session.get(models.Student, sid)
            if s:
                u = session.get(models.User, s.user_id)
                if search and u and search.lower() not in (u.full_name or "").lower() and search.lower() not in (s.admission_no or "").lower():
                    continue
                students.append({"student": s, "user": u})
        return students


@router.get("/portal/teacher/profile")
def teacher_portal_profile(current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        return {
            "id": teacher.id, "user_id": teacher.user_id, "employee_no": teacher.employee_no,
            "full_name": current_user.full_name, "email": current_user.email,
            "hire_date": teacher.hire_date, "is_active": teacher.is_active,
        }


@router.put("/portal/teacher/profile")
def teacher_update_profile(profile_update: dict, current_user=Depends(auth.require_roles("Teacher"))):
    if "full_name" in profile_update:
        crud.update_user(current_user.id, {"full_name": profile_update["full_name"]})
    return {"msg": "Profile updated"}


@router.post("/portal/teacher/change-password")
def teacher_change_password(data: schemas.PasswordChange, current_user=Depends(auth.require_roles("Teacher"))):
    if not auth.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    hashed = auth.get_password_hash(data.new_password)
    crud.update_user(current_user.id, {"hashed_password": hashed})
    return {"msg": "Password changed successfully"}


@router.get("/portal/teacher/attendance")
def teacher_portal_attendance(
    class_id: Optional[int] = None,
    date_filter: Optional[date] = None,
    current_user=Depends(auth.require_roles("Teacher"))
):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        query = select(models.Attendance)
        if class_id:
            enrollments = session.exec(select(models.Enrollment).where(models.Enrollment.class_id == class_id)).all()
            student_ids = [e.student_id for e in enrollments]
            if student_ids:
                query = query.where(models.Attendance.student_id.in_(student_ids))
            else:
                query = query.where(False)
        if date_filter:
            query = query.where(models.Attendance.date == date_filter)
        records = session.exec(query.order_by(models.Attendance.date.desc()).limit(200)).all()
        return records


@router.post("/portal/teacher/attendance")
def teacher_mark_attendance(attendance_in: schemas.AttendanceCreate, current_user=Depends(auth.require_roles("Teacher"))):
    return create_resource(attendance_in, models.Attendance, current_user)


@router.post("/portal/teacher/attendance/bulk")
def teacher_bulk_attendance(attendances: List[schemas.AttendanceCreate], current_user=Depends(auth.require_roles("Teacher"))):
    created = []
    for a in attendances:
        created.append(create_resource(a, models.Attendance, current_user))
    return created


@router.put("/portal/teacher/attendance/{attendance_id}")
def teacher_update_attendance(attendance_id: int, att_update: schemas.AttendanceUpdate, current_user=Depends(auth.require_roles("Teacher"))):
    att = update_resource(models.Attendance, attendance_id, att_update.dict(exclude_unset=True))
    if not att:
        raise HTTPException(404)
    return att


@router.get("/portal/teacher/homework")
def teacher_portal_homework(
    class_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    current_user=Depends(auth.require_roles("Teacher"))
):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        query = select(models.Homework).where(models.Homework.assigned_by == teacher.id)
        if class_id:
            query = query.where(models.Homework.class_id == class_id)
        homeworks = session.exec(query.order_by(models.Homework.due_date.desc()).offset(skip).limit(limit)).all()
        result = []
        for hw in homeworks:
            submission_count = session.exec(select(func.count(models.HomeworkSubmission.id)).where(models.HomeworkSubmission.homework_id == hw.id)).one() or 0
            result.append({"homework": hw, "submission_count": submission_count})
        return result


@router.post("/portal/teacher/homework")
def teacher_create_homework(hw_in: schemas.HomeworkCreate, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        hw_in.assigned_by = teacher.id
    return create_resource(hw_in, models.Homework, current_user)


@router.put("/portal/teacher/homework/{homework_id}")
def teacher_update_homework(homework_id: int, hw_update: schemas.HomeworkUpdate, current_user=Depends(auth.require_roles("Teacher"))):
    hw = update_resource(models.Homework, homework_id, hw_update.dict(exclude_unset=True))
    if not hw:
        raise HTTPException(404)
    return hw


@router.delete("/portal/teacher/homework/{homework_id}")
def teacher_delete_homework(homework_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    if not delete_resource(models.Homework, homework_id):
        raise HTTPException(404)
    return {}


@router.get("/portal/teacher/homework/{homework_id}/submissions")
def teacher_homework_submissions(homework_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        submissions = session.exec(select(models.HomeworkSubmission, models.Student, models.User)
            .join(models.Student, models.HomeworkSubmission.student_id == models.Student.id)
            .join(models.User, models.Student.user_id == models.User.id)
            .where(models.HomeworkSubmission.homework_id == homework_id)).all()
        return [{"submission": s, "student": st, "user": u} for s, st, u in submissions]


@router.put("/portal/teacher/homework/{homework_id}/submissions/{submission_id}/grade")
def teacher_grade_submission(homework_id: int, submission_id: int, grade: str, feedback: Optional[str] = None, current_user=Depends(auth.require_roles("Teacher"))):
    updates = {"grade": grade, "status": "graded"}
    if feedback:
        updates["feedback"] = feedback
    sub = update_resource(models.HomeworkSubmission, submission_id, updates)
    if not sub:
        raise HTTPException(404)
    return sub


@router.get("/portal/teacher/exams")
def teacher_portal_exams(class_id: Optional[int] = None, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        if not teacher:
            raise HTTPException(404, "Teacher not found")
        query = select(models.Exam)
        exams = session.exec(query.order_by(models.Exam.start_date.desc()).limit(50)).all()
        return exams


@router.post("/portal/teacher/exams")
def teacher_create_exam(exam_in: schemas.ExamCreate, current_user=Depends(auth.require_roles("Teacher"))):
    return create_resource(exam_in, models.Exam, current_user)


@router.put("/portal/teacher/exams/{exam_id}")
def teacher_update_exam(exam_id: int, exam_update: schemas.ExamUpdate, current_user=Depends(auth.require_roles("Teacher"))):
    exam = update_resource(models.Exam, exam_id, exam_update.dict(exclude_unset=True))
    if not exam:
        raise HTTPException(404)
    return exam


@router.delete("/portal/teacher/exams/{exam_id}")
def teacher_delete_exam(exam_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    if not delete_resource(models.Exam, exam_id):
        raise HTTPException(404)
    return {}


@router.post("/portal/teacher/exams/{exam_id}/marks")
def teacher_enter_marks(exam_id: int, result_in: schemas.ExamResultCreate, current_user=Depends(auth.require_roles("Teacher"))):
    result_in.exam_id = exam_id
    return create_resource(result_in, models.ExamResult, current_user)


@router.post("/portal/teacher/exams/{exam_id}/marks/bulk")
def teacher_bulk_marks(exam_id: int, results: List[schemas.ExamResultCreate], current_user=Depends(auth.require_roles("Teacher"))):
    created = []
    for r in results:
        r.exam_id = exam_id
        created.append(create_resource(r, models.ExamResult, current_user))
    return created


@router.put("/portal/teacher/exams/{exam_id}/marks/{result_id}")
def teacher_update_marks(exam_id: int, result_id: int, result_update: schemas.ExamResultUpdate, current_user=Depends(auth.require_roles("Teacher"))):
    r = update_resource(models.ExamResult, result_id, result_update.dict(exclude_unset=True))
    if not r:
        raise HTTPException(404)
    return r


@router.get("/portal/teacher/exams/{exam_id}/marks")
def teacher_exam_marks(exam_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        results = session.exec(select(models.ExamResult, models.Student, models.User, models.Subject)
            .join(models.Student, models.ExamResult.student_id == models.Student.id)
            .join(models.User, models.Student.user_id == models.User.id)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .where(models.ExamResult.exam_id == exam_id)).all()
        return [{"result": r, "student": s, "user": u, "subject": sub} for r, s, u, sub in results]


@router.post("/portal/teacher/exams/{exam_id}/publish")
def teacher_publish_results(exam_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    return {"msg": "Results published"}


@router.get("/portal/teacher/students/{student_id}/profile")
def teacher_student_profile(student_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        student = session.get(models.Student, student_id)
        if not student:
            raise HTTPException(404)
        user = session.get(models.User, student.user_id)
        enrollment = session.exec(select(models.Enrollment).where(models.Enrollment.student_id == student_id)).first()
        cls_name, sec_name = "", ""
        if enrollment:
            c = session.get(models.SchoolClass, enrollment.class_id)
            if c: cls_name = c.name
            s = session.get(models.Section, enrollment.section_id) if enrollment.section_id else None
            if s: sec_name = s.name
        return {"student": student, "user": user, "class_name": cls_name, "section_name": sec_name}


@router.get("/portal/teacher/students/{student_id}/attendance")
def teacher_student_attendance(student_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        records = session.exec(select(models.Attendance).where(models.Attendance.student_id == student_id).order_by(models.Attendance.date.desc()).limit(100)).all()
        total = len(records)
        present = len([r for r in records if r.status == "present"])
        pct = round((present / total * 100), 1) if total else 0
        return {"records": records, "percentage": pct}


@router.get("/portal/teacher/students/{student_id}/homework")
def teacher_student_homework(student_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        submissions = session.exec(select(models.HomeworkSubmission, models.Homework)
            .join(models.Homework, models.HomeworkSubmission.homework_id == models.Homework.id)
            .where(models.HomeworkSubmission.student_id == student_id)).all()
        return [{"submission": s, "homework": h} for s, h in submissions]


@router.get("/portal/teacher/students/{student_id}/performance")
def teacher_student_performance(student_id: int, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        results = session.exec(select(models.ExamResult, models.Subject, models.Exam)
            .join(models.Subject, models.ExamResult.subject_id == models.Subject.id)
            .join(models.Exam, models.ExamResult.exam_id == models.Exam.id)
            .where(models.ExamResult.student_id == student_id)).all()
        total_obtained = sum(r.marks_obtained or 0 for r, _, _ in results)
        total_max = sum(r.max_marks or 0 for r, _, _ in results)
        pct = round((total_obtained / total_max * 100), 1) if total_max else 0
        return {"results": [{"result": r, "subject": s, "exam": e} for r, s, e in results], "percentage": pct}


@router.post("/portal/teacher/notices")
def teacher_create_notice(notice_in: schemas.NoticeCreate, current_user=Depends(auth.require_roles("Teacher"))):
    notice_in.created_by = current_user.id
    return create_resource(notice_in, models.Notice, current_user)


@router.get("/portal/teacher/calendar")
def teacher_portal_calendar(current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        teacher = session.exec(select(models.Teacher).where(models.Teacher.user_id == current_user.id)).first()
        events = session.exec(select(models.Event).where(models.Event.start_date >= datetime.utcnow()).order_by(models.Event.start_date).limit(50)).all()
        exams = session.exec(select(models.Exam).where(models.Exam.start_date >= date.today()).order_by(models.Exam.start_date).limit(50)).all()
        timetable = []
        if teacher:
            timetable = session.exec(select(models.Timetable, models.Subject, models.SchoolClass, models.Section)
                .join(models.Subject, models.Timetable.subject_id == models.Subject.id)
                .join(models.SchoolClass, models.Timetable.class_id == models.SchoolClass.id)
                .outerjoin(models.Section, models.Timetable.section_id == models.Section.id)
                .where(models.Timetable.teacher_id == teacher.id)).all()
        return {"events": events, "exams": exams, "timetable": [{"entry": t, "subject": s, "class": c, "section": sec} for t, s, c, sec in timetable]}


@router.get("/portal/teacher/messages")
def teacher_portal_messages(skip: int = 0, limit: int = 50, search: Optional[str] = None, current_user=Depends(auth.require_roles("Teacher"))):
    with Session(engine) as session:
        query = select(models.Message).where(
            or_(models.Message.recipient_id == current_user.id, models.Message.sender_id == current_user.id)
        )
        if search:
            query = query.where(models.Message.subject.contains(search))
        messages = session.exec(query.order_by(models.Message.sent_on.desc()).offset(skip).limit(limit)).all()
        unread = session.exec(select(func.count(models.Message.id)).where(models.Message.recipient_id == current_user.id, models.Message.is_read == False)).one() or 0
        return {"messages": messages, "unread": unread}


@router.post("/portal/teacher/messages")
def teacher_send_message(msg_in: schemas.MessageCreate, current_user=Depends(auth.require_roles("Teacher"))):
    msg_in.sender_id = current_user.id
    return create_resource(msg_in, models.Message, current_user)


# ========== AUDIT LOG ==========
@router.get("/audit-logs", response_model=List[schemas.AuditLogRead])
def list_audit_logs(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles("Super Admin"))):
    return list_resource(models.AuditLog, skip=skip, limit=limit)


# ========== ANALYTICS ==========
@router.get("/analytics/overview")
def analytics_overview(current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    with Session(engine) as session:
        sid = get_current_school_id()
        
        student_stmt = select(func.count(models.Student.id))
        teacher_stmt = select(func.count(models.Teacher.id))
        male_stmt = select(func.count(models.Student.id)).where(models.Student.gender == "Male")
        female_stmt = select(func.count(models.Student.id)).where(models.Student.gender == "Female")
        fee_stmt = select(func.coalesce(func.sum(models.Payment.amount), 0))
        pass_stmt = select(func.count(models.ExamResult.id)).where(models.ExamResult.marks_obtained >= models.ExamResult.max_marks * 0.4)
        total_results_stmt = select(func.count(models.ExamResult.id))
        
        if sid is not None:
            student_stmt = student_stmt.where(models.Student.school_id == sid)
            teacher_stmt = teacher_stmt.where(models.Teacher.school_id == sid)
            male_stmt = male_stmt.where(models.Student.school_id == sid)
            female_stmt = female_stmt.where(models.Student.school_id == sid)
            fee_stmt = fee_stmt.where(models.Payment.school_id == sid)
            pass_stmt = pass_stmt.where(models.ExamResult.school_id == sid)
            total_results_stmt = total_results_stmt.where(models.ExamResult.school_id == sid)
        
        total_students = session.exec(student_stmt).one() or 0
        total_teachers = session.exec(teacher_stmt).one() or 0
        male = session.exec(male_stmt).one() or 0
        female = session.exec(female_stmt).one() or 0
        fee_collection = session.exec(fee_stmt).one() or 0
        pass_count = session.exec(pass_stmt).one() or 0
        total_results = session.exec(total_results_stmt).one() or 0
        pass_pct = round((pass_count / total_results * 100), 1) if total_results else 0
        return {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "male_students": male, "female_students": female,
            "fee_collection": float(fee_collection),
            "pass_percentage": pass_pct,
        }


@router.get("/search")
def global_search(q: str = Query(..., min_length=1), current_user: models.User = Depends(auth.get_current_user)):
    """Global search across students, teachers, classes, and sections."""
    school_id = get_current_school_id()
    results = []
    with Session(engine) as session:
        pattern = f"%{q}%"

        students = session.exec(
            select(models.Student).where(
                models.Student.school_id == school_id,
                or_(
                    models.Student.admission_no.like(pattern),
                    models.User.full_name.like(pattern),
                )
            ).join(models.User, models.Student.user_id == models.User.id, isouter=True).limit(10)
        ).all()
        for s in students:
            user = session.get(models.User, s.user_id) if s.user_id else None
            results.append({
                "title": user.full_name if user else f"Student #{s.id}",
                "subtitle": f"Admission: {s.admission_no or 'N/A'}",
                "icon": "👨‍🎓",
                "url": f"/students/{s.id}",
            })

        teachers = session.exec(
            select(models.User).where(
                models.User.school_id == school_id,
                models.User.role == "Teacher",
                models.User.full_name.like(pattern),
            ).limit(10)
        ).all()
        for t in teachers:
            results.append({
                "title": t.full_name,
                "subtitle": "Teacher",
                "icon": "👩‍🏫",
                "url": f"/teachers/{t.id}",
            })

        classes = session.exec(
            select(models.SchoolClass).where(
                models.SchoolClass.school_id == school_id,
                models.SchoolClass.name.like(pattern),
            ).limit(10)
        ).all()
        for c in classes:
            results.append({
                "title": c.name,
                "subtitle": f"Class (Grade: {c.grade_level or 'N/A'})",
                "icon": "🏫",
                "url": f"/classes/{c.id}",
            })

        sections = session.exec(
            select(models.Section).where(
                models.Section.school_id == school_id,
                models.Section.name.like(pattern),
            ).limit(10)
        ).all()
        for s in sections:
            results.append({
                "title": s.name,
                "subtitle": "Section",
                "icon": "📂",
                "url": f"/sections/{s.id}",
            })

    return {"results": results}
