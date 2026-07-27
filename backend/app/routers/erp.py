from typing import List
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status

from .. import models, schemas, crud, auth
from ..database import engine

router = APIRouter()

ADMIN_ROLES = ("Super Admin", "School Admin", "Principal")
ALL_ADMIN_ROLES = ("Super Admin", "School Admin", "Principal", "Teacher")


def create_resource(resource_in, model):
    resource = model(**resource_in.dict())
    return crud.create_item(resource)


def get_resource(model, resource_id: int):
    return crud.get_item(model, resource_id)


def list_resource(model, skip: int = 0, limit: int = 100):
    return crud.list_items(model, skip=skip, limit=limit)


def update_resource(model, resource_id: int, values: dict):
    return crud.update_item(model, resource_id, values)


def delete_resource(model, resource_id: int):
    return crud.delete_item(model, resource_id)


# Parent endpoints
@router.post("/parents", response_model=schemas.ParentRead, status_code=status.HTTP_201_CREATED)
def create_parent(parent_in: schemas.ParentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    parent = create_resource(parent_in, models.Parent)
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


@router.put("/parents/{parent_id}", response_model=schemas.ParentRead)
def update_parent(parent_id: int, parent_update: schemas.ParentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    parent = update_resource(models.Parent, parent_id, parent_update.dict(exclude_unset=True))
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    return parent


@router.delete("/parents/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parent(parent_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    if not delete_resource(models.Parent, parent_id):
        raise HTTPException(status_code=404, detail="Parent not found")
    return {}


# Teacher endpoints
@router.post("/teachers", response_model=schemas.TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher_in: schemas.TeacherCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    teacher = create_resource(teacher_in, models.Teacher)
    return teacher


@router.get("/teachers", response_model=List[schemas.TeacherRead])
def list_teachers(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return list_resource(models.Teacher, skip=skip, limit=limit)


@router.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    teacher = get_resource(models.Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


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
    student = create_resource(student_in, models.Student)
    return student


@router.get("/students", response_model=List[schemas.StudentRead])
def list_students(skip: int = 0, limit: int = 100, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    return list_resource(models.Student, skip=skip, limit=limit)


@router.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES, *ALL_ADMIN_ROLES))):
    student = get_resource(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


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


# Academic year endpoints
@router.post("/academic-years", response_model=schemas.AcademicYearRead, status_code=status.HTTP_201_CREATED)
def create_academic_year(year_in: schemas.AcademicYearCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    year = create_resource(year_in, models.AcademicYear)
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
    school_class = create_resource(class_in, models.SchoolClass)
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
    section = create_resource(section_in, models.Section)
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
    subject = create_resource(subject_in, models.Subject)
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


# Subject allocation endpoints
@router.post("/subject-allocations", response_model=schemas.SubjectAllocationRead, status_code=status.HTTP_201_CREATED)
def create_subject_allocation(allocation_in: schemas.SubjectAllocationCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    allocation = create_resource(allocation_in, models.SubjectAllocation)
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
    enrollment = create_resource(enrollment_in, models.Enrollment)
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
    attendance = create_resource(attendance_in, models.Attendance)
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
    homework = create_resource(homework_in, models.Homework)
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
    exam = create_resource(exam_in, models.Exam)
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
    result = create_resource(result_in, models.ExamResult)
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
    fee_structure = create_resource(fee_structure_in, models.FeeStructure)
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
    assignment = create_resource(fee_assignment_in, models.FeeAssignment)
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
    payment = create_resource(payment_in, models.Payment)
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
    notice = create_resource(notice_in, models.Notice)
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
    message = create_resource(message_in, models.Message)
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
    event = create_resource(event_in, models.Event)
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
    certificate = create_resource(certificate_in, models.Certificate)
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
    document = create_resource(document_in, models.Document)
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
