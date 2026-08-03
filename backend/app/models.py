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
    principal_name: Optional[str] = None
    theme_color: Optional[str] = Field(default="#4f46e5")
    stamp_path: Optional[str] = None
    signature_path: Optional[str] = None
    academic_year_id: Optional[int] = Field(default=None, foreign_key="academicyear.id")


class Room(SQLModel, table=True):
    __tablename__ = "room"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    room_name: str = Field(index=True)
    room_number: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    room_type: Optional[str] = Field(default="Classroom")  # Classroom, Lab, Computer Lab, Library, Auditorium, Sports Hall
    color: Optional[str] = None  # UI color for room in timetable
    is_active: bool = True
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class PeriodMaster(SQLModel, table=True):
    __tablename__ = "period_master"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    period_name: str  # e.g., "Period 1", "Lunch", "Assembly"
    period_number: int  # 1-based period number
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    is_break: bool = False
    is_assembly: bool = False
    is_sports: bool = False
    is_library: bool = False
    is_practical: bool = False
    sort_order: int = 0
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class TeacherAvailability(SQLModel, table=True):
    __tablename__ = "teacher_availability"
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.id")
    school_id: int = Field(foreign_key="school.id", index=True)
    day_of_week: int  # 0=Monday, 6=Sunday
    period_number: int  # 1-based period number
    is_available: bool = True  # True = available, False = unavailable
    availability_type: str = Field(default="available")  # available, unavailable, leave, preferred
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class Timetable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    academic_year_id: int = Field(foreign_key="academicyear.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    subject_id: int = Field(foreign_key="subject.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    day_of_week: int  # 0=Monday, 6=Sunday
    period: int  # 1-based period number
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None    # HH:MM format
    status: str = Field(default="active")  # active, cancelled, rescheduled
    remarks: Optional[str] = None
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class TimetableGeneratorLog(SQLModel, table=True):
    __tablename__ = "timetable_generator_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    academic_year_id: int = Field(foreign_key="academicyear.id")
    generated_by: Optional[int] = Field(default=None, foreign_key="user.id")
    generation_type: str = Field(default="auto")  # auto, manual, copy, duplicate
    source_academic_year_id: Optional[int] = Field(default=None, foreign_key="academicyear.id")
    source_section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    config: Optional[str] = None  # JSON string of generation config
    result_summary: Optional[str] = None  # JSON string of generation results
    conflicts_found: int = 0
    conflicts_resolved: int = 0
    status: str = Field(default="completed")  # completed, partial, failed
    created_on: datetime = Field(default_factory=datetime.utcnow)


class TimetableConflictLog(SQLModel, table=True):
    __tablename__ = "timetable_conflict_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    academic_year_id: int = Field(foreign_key="academicyear.id")
    conflict_type: str  # teacher, room, class, section, subject, period
    conflict_description: str
    day_of_week: int
    period_number: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id")
    class_id: Optional[int] = Field(default=None, foreign_key="schoolclass.id")
    section_id: Optional[int] = Field(default=None, foreign_key="section.id")
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")
    conflicting_record_id: Optional[int] = None
    resolved: bool = False
    resolved_by: Optional[int] = Field(default=None, foreign_key="user.id")
    resolved_at: Optional[datetime] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)


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
    __tablename__ = "auditlog"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    school_id: Optional[int] = Field(default=None, foreign_key="school.id", index=True)
    action: str = Field(index=True)
    resource: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    before_values: Optional[str] = None
    after_values: Optional[str] = None
    ip_address: Optional[str] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)


class GradingRule(SQLModel, table=True):
    """Configurable grading rules per school."""
    __tablename__ = "grading_rule"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    grading_scale: str = Field(default="10_point")  # 10_point, 4_point, 5_point, custom
    rules_json: str  # JSON array of grading rules
    pass_percentage: float = Field(default=33.0)
    is_active: bool = True
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class ReportCard(SQLModel, table=True):
    __tablename__ = "report_card"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    exam_id: int = Field(foreign_key="exam.id", index=True)
    class_id: Optional[int] = Field(default=None, foreign_key="schoolclass.id", index=True)
    academic_year_id: int = Field(foreign_key="academicyear.id", index=True)
    template_id: Optional[int] = Field(default=None, foreign_key="report_card_template.id")
    total_marks: float = Field(default=0.0)
    obtained_marks: float = Field(default=0.0)
    percentage: float = Field(default=0.0)
    overall_grade: Optional[str] = None
    gpa: float = Field(default=0.0)
    attendance_percentage: float = Field(default=0.0)
    working_days: int = Field(default=0)
    present_days: int = Field(default=0)
    teacher_remarks: Optional[str] = None
    principal_remarks: Optional[str] = None
    result_status: Optional[str] = None  # PASS, FAIL, PROMOTED, DETENTION
    promotion_status: Optional[str] = None
    rank: Optional[int] = None
    verification_id: str = Field(unique=True, index=True)
    pdf_path: Optional[str] = None
    is_regenerated: bool = False
    status: str = Field(default="draft")  # draft, generated, published, archived
    generated_by: Optional[int] = Field(default=None, foreign_key="user.id")
    generated_on: datetime = Field(default_factory=datetime.utcnow)
    published_on: Optional[datetime] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class ReportCardSubject(SQLModel, table=True):
    __tablename__ = "report_card_subject"
    id: Optional[int] = Field(default=None, primary_key=True)
    report_card_id: int = Field(foreign_key="report_card.id", index=True)
    subject_id: int = Field(foreign_key="subject.id")
    subject_name: Optional[str] = None
    maximum_marks: float = Field(default=0.0)
    obtained_marks: float = Field(default=0.0)
    percentage: float = Field(default=0.0)
    grade: Optional[str] = None
    grade_point: float = Field(default=0.0)
    remarks: Optional[str] = None
    school_id: int = Field(foreign_key="school.id", index=True)
    examination_type_id: Optional[int] = Field(default=None, foreign_key="examination_type.id")
    grade_scale_range_id: Optional[int] = Field(default=None, foreign_key="grade_scale_range.id")
    teacher_remark: Optional[str] = None
    is_passing: Optional[bool] = None
    credit_hours: Optional[float] = None
    weightage: Optional[float] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)


# ========== REPORT CARD TEMPLATES (Enterprise) ==========

class ReportCardTemplate(SQLModel, table=True):
    __tablename__ = "report_card_template"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    name: str
    description: Optional[str] = None
    template_type: str = Field(default="standard")
    academic_year_id: Optional[int] = Field(default=None, foreign_key="academicyear.id")
    class_id: Optional[int] = Field(default=None, foreign_key="schoolclass.id")
    exam_id: Optional[int] = Field(default=None, foreign_key="exam.id")
    is_default: bool = False
    is_archived: bool = False
    version: int = 1
    parent_template_id: Optional[int] = Field(default=None, foreign_key="report_card_template.id")
    config: Optional[str] = None
    header_config: Optional[str] = None
    footer_config: Optional[str] = None
    body_config: Optional[str] = None
    css_config: Optional[str] = None
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class ReportCardTemplateVersion(SQLModel, table=True):
    __tablename__ = "report_card_template_version"
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="report_card_template.id")
    school_id: int = Field(foreign_key="school.id", index=True)
    version: int
    config: Optional[str] = None
    header_config: Optional[str] = None
    footer_config: Optional[str] = None
    body_config: Optional[str] = None
    css_config: Optional[str] = None
    change_description: Optional[str] = None
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_on: datetime = Field(default_factory=datetime.utcnow)


class ReportCardComponent(SQLModel, table=True):
    __tablename__ = "report_card_component"
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="report_card_template.id")
    school_id: int = Field(foreign_key="school.id", index=True)
    component_type: str  # logo, student_photo, qr_code, signature, subject_table, chart, remarks, attendance, watermark, header, footer, custom_text, custom_image
    label: str
    x_position: float = 0.0  # percentage from left
    y_position: float = 0.0  # percentage from top
    width: float = 100.0  # percentage of page width
    height: float = 50.0  # percentage of page height
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    font_family: Optional[str] = None
    font_weight: Optional[str] = None
    border_radius: Optional[int] = None
    border_width: Optional[int] = None
    border_color: Optional[str] = None
    background_color: Optional[str] = None
    margin_top: Optional[float] = None
    margin_bottom: Optional[float] = None
    margin_left: Optional[float] = None
    margin_right: Optional[float] = None
    padding: Optional[float] = None
    is_visible: bool = True
    is_editable: bool = True
    data_source: Optional[str] = None  # JSON path or field reference
    default_value: Optional[str] = None
    sort_order: int = 0
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


# ========== EXAMINATION TYPES ==========

class ExaminationType(SQLModel, table=True):
    __tablename__ = "examination_type"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    name: str  # Unit Test, Monthly Test, Mid Term, Half Yearly, Annual, etc.
    code: Optional[str] = None
    exam_type: str = Field(default="theory")  # theory, practical, viva, internal_assessment, assignment, project
    weightage: float = 0.0  # percentage weightage
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: bool = True
    is_published: bool = False
    show_in_report_card: bool = True
    sort_order: int = 0
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class ExamWeightageConfig(SQLModel, table=True):
    __tablename__ = "exam_weightage_config"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    academic_year_id: int = Field(foreign_key="academicyear.id")
    class_id: int = Field(foreign_key="schoolclass.id")
    exam_type_id: int = Field(foreign_key="examination_type.id")
    weightage: float = 0.0  # percentage
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None
    is_active: bool = True
    created_on: datetime = Field(default_factory=datetime.utcnow)


# ========== GRADE ENGINE ==========

class GradeScale(SQLModel, table=True):
    __tablename__ = "grade_scale"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    name: str  # e.g., "CBSE Grade Scale", "Custom 10-Point"
    scale_type: str = Field(default="percentage")  # percentage, gpa, letter, competency, descriptive, rubric
    min_value: float = 0.0
    max_value: float = 100.0
    passing_value: float = 40.0
    is_default: bool = False
    is_active: bool = True
    created_on: datetime = Field(default_factory=datetime.utcnow)


class GradeScaleRange(SQLModel, table=True):
    __tablename__ = "grade_scale_range"
    id: Optional[int] = Field(default=None, primary_key=True)
    grade_scale_id: int = Field(foreign_key="grade_scale.id")
    school_id: int = Field(foreign_key="school.id", index=True)
    grade: str  # A+, A, B+, B, C+, C, D, E, F or 4.0, 3.5, 3.0, etc.
    grade_point: Optional[float] = None  # GPA value
    min_mark: float
    max_mark: float
    description: Optional[str] = None  # e.g., "Excellent", "Good", "Average"
    is_passing: bool = True
    sort_order: int = 0


class GpaEngineConfig(SQLModel, table=True):
    __tablename__ = "gpa_engine_config"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    name: str  # e.g., "4-Point Scale", "5-Point Scale", "10-Point Scale"
    scale_type: str = Field(default="4_point")  # 4_point, 5_point, 10_point, percentage, weighted, credit_based
    max_gpa: float = 4.0
    min_gpa: float = 0.0
    grade_point_decimals: int = 2
    credit_based: bool = False
    weighted: bool = False
    formula_config: Optional[str] = None  # JSON string of formula configuration
    is_active: bool = True
    created_on: datetime = Field(default_factory=datetime.utcnow)


class GpaGradeMapping(SQLModel, table=True):
    __tablename__ = "gpa_grade_mapping"
    id: Optional[int] = Field(default=None, primary_key=True)
    gpa_engine_id: int = Field(foreign_key="gpa_engine_config.id")
    school_id: int = Field(foreign_key="school.id", index=True)
    grade: str
    grade_point: float
    min_percentage: float
    max_percentage: float
    description: Optional[str] = None
    is_passing: bool = True
    sort_order: int = 0


# ========== SUBJECT CATEGORIES ==========

class SubjectCategory(SQLModel, table=True):
    __tablename__ = "subject_category"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    name: str  # Languages, Science, Commerce, Arts, etc.
    code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_on: datetime = Field(default_factory=datetime.utcnow)


class SubjectCategoryMapping(SQLModel, table=True):
    __tablename__ = "subject_category_mapping"
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id", index=True)
    subject_id: int = Field(foreign_key="subject.id")
    category_id: int = Field(foreign_key="subject_category.id")
    is_primary: bool = True  # Whether this is the primary category for the subject
    created_on: datetime = Field(default_factory=datetime.utcnow)


# ========== REPORT CARDS ==========
