from typing import Optional
from datetime import date, datetime
from sqlmodel import SQLModel, Field


class School(SQLModel, table=True):
    __tablename__ = "school"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_name: str = Field(index=True)
    school_code: str = Field(unique=True, index=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    subscription_plan: Optional[str] = Field(default="free")
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    status: str = Field(default="active")  # active, suspended, expired
    timezone: Optional[str] = Field(default="UTC")
    currency: Optional[str] = Field(default="USD")
    student_limit: Optional[int] = Field(default=0)
    teacher_limit: Optional[int] = Field(default=0)
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    role: Optional[str] = Field(default="Student")
    school_id: int = Field(foreign_key="school.id", index=True)


class Parent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    phone: Optional[str] = None
    address: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    employee_no: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: bool = True
    school_id: int = Field(foreign_key="school.id", index=True)


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
    school_id: int = Field(foreign_key="school.id", index=True)


class AcademicYear(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_date: date
    end_date: date
    is_active: bool = False
    school_id: int = Field(foreign_key="school.id", index=True)


class SchoolClass(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    grade_level: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Section(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    class_id: int = Field(foreign_key="schoolclass.id")
    school_id: int = Field(foreign_key="school.id", index=True)


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class SubjectAllocation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    school_id: int = Field(foreign_key="school.id", index=True)


class Enrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    academic_year_id: int = Field(foreign_key="academicyear.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    enrolled_on: datetime = Field(default_factory=datetime.utcnow)
    school_id: int = Field(foreign_key="school.id", index=True)


class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    date: date
    status: str = Field(default="present")
    remarks: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Homework(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    assigned_by: int = Field(foreign_key="teacher.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    due_date: Optional[date] = None
    attachment_path: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


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
    school_id: int = Field(foreign_key="school.id", index=True)


class TeacherAttendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.id")
    date: date
    status: str = Field(default="present")
    remarks: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    academic_year_id: int = Field(foreign_key="academicyear.id")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class ExamResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exam_id: int = Field(foreign_key="exam.id")
    student_id: int = Field(foreign_key="student.id")
    subject_id: int = Field(foreign_key="subject.id")
    marks_obtained: Optional[float] = None
    max_marks: Optional[float] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class FeeStructure(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    amount: float
    category: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class FeeAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    fee_structure_id: int = Field(foreign_key="feestructure.id")
    due_date: Optional[date] = None
    is_paid: bool = False
    school_id: int = Field(foreign_key="school.id", index=True)


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fee_assignment_id: int = Field(foreign_key="feeassignment.id")
    amount: float
    paid_on: datetime = Field(default_factory=datetime.utcnow)
    reference: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Notice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: Optional[str] = None
    target_roles: Optional[str] = None  # comma-separated roles or "all"
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_on: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = None
    attachments_path: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str
    body: Optional[str] = None
    sender_id: int = Field(foreign_key="user.id")
    recipient_id: int = Field(foreign_key="user.id")
    sent_on: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False
    school_id: int = Field(foreign_key="school.id", index=True)


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    event_type: Optional[str] = None
    target_roles: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Certificate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    certificate_type: str
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    remarks: Optional[str] = None
    file_path: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_type: str
    owner_id: int
    name: str
    file_path: str
    uploaded_on: datetime = Field(default_factory=datetime.utcnow)
    school_id: int = Field(foreign_key="school.id", index=True)


class SchoolSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True, unique=True)
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
    school_id: int = Field(foreign_key="school.id", index=True)


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: Optional[str] = None
    notification_type: Optional[str] = None
    category: Optional[str] = None
    title: str
    message: str
    priority: Optional[str] = Field(default="normal")
    related_module: Optional[str] = None
    related_record_id: Optional[int] = None
    action_url: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sender_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_read: bool = False
    is_archived: bool = False
    is_deleted: bool = False
    is_pinned: bool = False
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class NotificationPreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    email_enabled: bool = True
    in_app_enabled: bool = True
    sound_enabled: bool = True
    browser_enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    category_preferences: Optional[str] = None
    digest_frequency: Optional[str] = Field(default="instant")
    push_enabled: bool = False


class DeviceToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    device_type: Optional[str] = None
    token: str = Field(index=True)
    platform: Optional[str] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)


class NotificationAuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    notification_id: int = Field(foreign_key="notification.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    details: Optional[str] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    school_id: Optional[int] = Field(default=None, foreign_key="school.id", index=True)
    action: str
    resource: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    before_values: Optional[str] = None
    after_values: Optional[str] = None
    ip_address: Optional[str] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)
