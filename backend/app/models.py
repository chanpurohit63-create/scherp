from typing import Optional
from datetime import date, datetime
from sqlmodel import SQLModel, Field


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    role: Optional[str] = Field(default="Student")


class Parent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    phone: Optional[str] = None
    address: Optional[str] = None


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    employee_no: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: bool = True


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    admission_no: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    admission_date: Optional[date] = None
    status: str = Field(default="active")
    father_id: Optional[int] = Field(default=None, foreign_key="parent.id")
    mother_id: Optional[int] = Field(default=None, foreign_key="parent.id")
    photo_path: Optional[str] = None


class AcademicYear(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_date: date
    end_date: date
    is_active: bool = False


class SchoolClass(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    grade_level: Optional[str] = None


class Section(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    class_id: int = Field(foreign_key="schoolclass.id")


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: Optional[str] = None


class SubjectAllocation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")


class Enrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    academic_year_id: int = Field(foreign_key="academicyear.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    enrolled_on: datetime = Field(default_factory=datetime.utcnow)


class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    date: date
    status: str = Field(default="present")
    remarks: Optional[str] = None


class Homework(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    assigned_by: int = Field(foreign_key="teacher.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    due_date: Optional[date] = None
    attachment_path: Optional[str] = None


class HomeworkSubmission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    homework_id: int = Field(foreign_key="homework.id")
    student_id: int = Field(foreign_key="student.id")
    submitted_on: datetime = Field(default_factory=datetime.utcnow)
    attachment_path: Optional[str] = None
    remarks: Optional[str] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None
    status: str = Field(default="submitted")


class TeacherAttendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.id")
    date: date
    status: str = Field(default="present")
    remarks: Optional[str] = None


class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    academic_year_id: int = Field(foreign_key="academicyear.id")
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ExamResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exam_id: int = Field(foreign_key="exam.id")
    student_id: int = Field(foreign_key="student.id")
    subject_id: int = Field(foreign_key="subject.id")
    marks_obtained: Optional[float] = None
    max_marks: Optional[float] = None


class FeeStructure(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    amount: float
    category: Optional[str] = None


class FeeAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    fee_structure_id: int = Field(foreign_key="feestructure.id")
    due_date: Optional[date] = None
    is_paid: bool = False


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fee_assignment_id: int = Field(foreign_key="feeassignment.id")
    amount: float
    paid_on: datetime = Field(default_factory=datetime.utcnow)
    reference: Optional[str] = None


class Notice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: Optional[str] = None
    target_roles: Optional[str] = None  # comma-separated roles or "all"
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_on: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = None
    attachments_path: Optional[str] = None


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str
    body: Optional[str] = None
    sender_id: int = Field(foreign_key="user.id")
    recipient_id: int = Field(foreign_key="user.id")
    sent_on: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    event_type: Optional[str] = None
    target_roles: Optional[str] = None


class Certificate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    certificate_type: str
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    remarks: Optional[str] = None
    file_path: Optional[str] = None


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_type: str
    owner_id: int
    name: str
    file_path: str
    uploaded_on: datetime = Field(default_factory=datetime.utcnow)


class SchoolSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_path: Optional[str] = None
    academic_year_id: Optional[int] = Field(default=None, foreign_key="academicyear.id")


class Timetable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    subject_id: int = Field(foreign_key="subject.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    day_of_week: int  # 0=Monday, 6=Sunday
    period: int  # 1-based period number
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    academic_year_id: int = Field(foreign_key="academicyear.id")


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    message: str
    notification_type: Optional[str] = None
    reference_id: Optional[int] = None
    is_read: bool = False
    created_on: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    resource: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)

