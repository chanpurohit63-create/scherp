from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "Student"


class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class ParentCreate(BaseModel):
    user_id: int
    phone: Optional[str] = None
    address: Optional[str] = None


class ParentRead(BaseModel):
    id: int
    user_id: int
    phone: Optional[str]
    address: Optional[str]

    class Config:
        orm_mode = True


class ParentProfileRead(ParentRead):
    email: EmailStr
    full_name: Optional[str]
    role: str


class ParentUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None


class TeacherCreate(BaseModel):
    user_id: int
    employee_no: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: Optional[bool] = True


class TeacherRead(BaseModel):
    id: int
    user_id: int
    employee_no: Optional[str]
    hire_date: Optional[date]
    is_active: bool

    class Config:
        orm_mode = True


class TeacherProfileRead(TeacherRead):
    email: EmailStr
    full_name: Optional[str]
    role: str


class TeacherUpdate(BaseModel):
    employee_no: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: Optional[bool] = None


class StudentCreate(BaseModel):
    user_id: int
    admission_no: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    admission_date: Optional[date] = None
    status: Optional[str] = "active"
    father_id: Optional[int] = None
    mother_id: Optional[int] = None


class StudentRead(BaseModel):
    id: int
    user_id: int
    admission_no: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    admission_date: Optional[date]
    status: str
    father_id: Optional[int]
    mother_id: Optional[int]
    photo_path: Optional[str]

    class Config:
        orm_mode = True


class StudentProfileRead(StudentRead):
    email: EmailStr
    full_name: Optional[str]
    role: str


class StudentUpdate(BaseModel):
    admission_no: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    admission_date: Optional[date] = None
    status: Optional[str] = None
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    photo_path: Optional[str] = None


class AcademicYearCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_active: Optional[bool] = False


class AcademicYearRead(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool

    class Config:
        orm_mode = True


class AcademicYearUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class SchoolClassCreate(BaseModel):
    name: str
    grade_level: Optional[str] = None


class SchoolClassRead(BaseModel):
    id: int
    name: str
    grade_level: Optional[str]

    class Config:
        orm_mode = True


class SchoolClassUpdate(BaseModel):
    name: Optional[str] = None
    grade_level: Optional[str] = None


class SectionCreate(BaseModel):
    name: str
    class_id: int


class SectionRead(BaseModel):
    id: int
    name: str
    class_id: int

    class Config:
        orm_mode = True


class SectionUpdate(BaseModel):
    name: Optional[str] = None
    class_id: Optional[int] = None


class SubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None


class SubjectRead(BaseModel):
    id: int
    name: str
    code: Optional[str]

    class Config:
        orm_mode = True


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class SubjectAllocationCreate(BaseModel):
    subject_id: int
    teacher_id: int
    class_id: int
    section_id: Optional[int] = None


class SubjectAllocationRead(BaseModel):
    id: int
    subject_id: int
    teacher_id: int
    class_id: int
    section_id: Optional[int]

    class Config:
        orm_mode = True


class SubjectAllocationUpdate(BaseModel):
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None


class EnrollmentCreate(BaseModel):
    student_id: int
    academic_year_id: int
    class_id: int
    section_id: Optional[int] = None


class EnrollmentRead(BaseModel):
    id: int
    student_id: int
    academic_year_id: int
    class_id: int
    section_id: Optional[int]
    enrolled_on: datetime

    class Config:
        orm_mode = True


class EnrollmentUpdate(BaseModel):
    student_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None


class AttendanceCreate(BaseModel):
    student_id: int
    date: date
    status: Optional[str] = "present"
    remarks: Optional[str] = None


class AttendanceRead(BaseModel):
    id: int
    student_id: int
    date: date
    status: str
    remarks: Optional[str]

    class Config:
        orm_mode = True


class AttendanceUpdate(BaseModel):
    date: Optional[date] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class HomeworkCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_by: int
    class_id: int
    section_id: Optional[int] = None
    due_date: Optional[date] = None
    attachment_path: Optional[str] = None


class HomeworkRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_by: int
    class_id: int
    section_id: Optional[int]
    due_date: Optional[date]
    attachment_path: Optional[str]

    class Config:
        orm_mode = True


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_by: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    due_date: Optional[date] = None
    attachment_path: Optional[str] = None


class HomeworkSubmissionCreate(BaseModel):
    homework_id: int
    student_id: int
    attachment_path: Optional[str] = None
    remarks: Optional[str] = None


class HomeworkSubmissionRead(BaseModel):
    id: int
    homework_id: int
    student_id: int
    submitted_on: datetime
    attachment_path: Optional[str]
    remarks: Optional[str]
    grade: Optional[str]
    feedback: Optional[str]
    status: str

    class Config:
        orm_mode = True


class HomeworkSubmissionUpdate(BaseModel):
    attachment_path: Optional[str] = None
    remarks: Optional[str] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None
    status: Optional[str] = None


class TeacherAttendanceCreate(BaseModel):
    teacher_id: int
    date: date
    status: Optional[str] = "present"
    remarks: Optional[str] = None


class TeacherAttendanceRead(BaseModel):
    id: int
    teacher_id: int
    date: date
    status: str
    remarks: Optional[str]

    class Config:
        orm_mode = True


class TeacherAttendanceUpdate(BaseModel):
    date: Optional[date] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class ExamCreate(BaseModel):
    name: str
    academic_year_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ExamRead(BaseModel):
    id: int
    name: str
    academic_year_id: int
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        orm_mode = True


class ExamUpdate(BaseModel):
    name: Optional[str] = None
    academic_year_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ExamResultCreate(BaseModel):
    exam_id: int
    student_id: int
    subject_id: int
    marks_obtained: Optional[float] = None
    max_marks: Optional[float] = None


class ExamResultRead(BaseModel):
    id: int
    exam_id: int
    student_id: int
    subject_id: int
    marks_obtained: Optional[float]
    max_marks: Optional[float]

    class Config:
        orm_mode = True


class ExamResultUpdate(BaseModel):
    exam_id: Optional[int] = None
    student_id: Optional[int] = None
    subject_id: Optional[int] = None
    marks_obtained: Optional[float] = None
    max_marks: Optional[float] = None


class FeeStructureCreate(BaseModel):
    name: str
    amount: float
    category: Optional[str] = None


class FeeStructureRead(BaseModel):
    id: int
    name: str
    amount: float
    category: Optional[str]

    class Config:
        orm_mode = True


class FeeStructureUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None


class FeeAssignmentCreate(BaseModel):
    student_id: int
    fee_structure_id: int
    due_date: Optional[date] = None
    is_paid: Optional[bool] = False


class FeeAssignmentRead(BaseModel):
    id: int
    student_id: int
    fee_structure_id: int
    due_date: Optional[date]
    is_paid: bool

    class Config:
        orm_mode = True


class FeeAssignmentUpdate(BaseModel):
    student_id: Optional[int] = None
    fee_structure_id: Optional[int] = None
    due_date: Optional[date] = None
    is_paid: Optional[bool] = None


class PaymentCreate(BaseModel):
    fee_assignment_id: int
    amount: float
    reference: Optional[str] = None


class PaymentRead(BaseModel):
    id: int
    fee_assignment_id: int
    amount: float
    paid_on: datetime
    reference: Optional[str]

    class Config:
        orm_mode = True


class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    reference: Optional[str] = None


class NoticeCreate(BaseModel):
    title: str
    content: Optional[str] = None
    target_roles: Optional[str] = None
    created_by: Optional[int] = None
    scheduled_for: Optional[datetime] = None
    attachments_path: Optional[str] = None


class NoticeRead(BaseModel):
    id: int
    title: str
    content: Optional[str]
    target_roles: Optional[str]
    created_by: Optional[int]
    created_on: datetime
    scheduled_for: Optional[datetime]
    attachments_path: Optional[str]

    class Config:
        orm_mode = True


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    target_roles: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    attachments_path: Optional[str] = None


class MessageCreate(BaseModel):
    subject: str
    body: Optional[str] = None
    sender_id: int
    recipient_id: int


class MessageRead(BaseModel):
    id: int
    subject: str
    body: Optional[str]
    sender_id: int
    recipient_id: int
    sent_on: datetime
    is_read: bool

    class Config:
        orm_mode = True


class MessageUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    is_read: Optional[bool] = None


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    event_type: Optional[str] = None
    target_roles: Optional[str] = None


class EventRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    event_type: Optional[str]
    target_roles: Optional[str]

    class Config:
        orm_mode = True


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[str] = None
    target_roles: Optional[str] = None


class CertificateCreate(BaseModel):
    student_id: int
    certificate_type: str
    issue_date: Optional[datetime] = None
    remarks: Optional[str] = None
    file_path: Optional[str] = None


class CertificateRead(BaseModel):
    id: int
    student_id: int
    certificate_type: str
    issue_date: datetime
    remarks: Optional[str]
    file_path: Optional[str]

    class Config:
        orm_mode = True


class CertificateUpdate(BaseModel):
    certificate_type: Optional[str] = None
    issue_date: Optional[datetime] = None
    remarks: Optional[str] = None
    file_path: Optional[str] = None


class SchoolSettingsRead(BaseModel):
    id: int
    school_name: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    logo_path: Optional[str]
    academic_year_id: Optional[int]

    class Config:
        orm_mode = True


class SchoolSettingsUpdate(BaseModel):
    school_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_path: Optional[str] = None
    academic_year_id: Optional[int] = None


class DashboardSummaryRead(BaseModel):
    total_students: int
    total_teachers: int
    attendance_percentage: float
    fee_collection: float
    pending_fees: int
    upcoming_exams: int
    upcoming_events: int
    notices: List[NoticeRead]
    monthly_attendance: List[dict]
    monthly_fee_collection: List[dict]
    student_growth: List[dict]
    exam_performance: List[dict]


class DocumentCreate(BaseModel):
    owner_type: str
    owner_id: int
    name: str
    file_path: str


class DocumentRead(BaseModel):
    id: int
    owner_type: str
    owner_id: int
    name: str
    file_path: str
    uploaded_on: datetime

    class Config:
        orm_mode = True


class DocumentUpdate(BaseModel):
    owner_type: Optional[str] = None
    owner_id: Optional[int] = None
    name: Optional[str] = None
    file_path: Optional[str] = None


class TimetableCreate(BaseModel):
    class_id: int
    section_id: Optional[int] = None
    subject_id: int
    teacher_id: int
    day_of_week: int
    period: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    academic_year_id: int


class TimetableRead(BaseModel):
    id: int
    class_id: int
    section_id: Optional[int]
    subject_id: int
    teacher_id: int
    day_of_week: int
    period: int
    start_time: Optional[str]
    end_time: Optional[str]
    room: Optional[str]
    academic_year_id: int

    class Config:
        orm_mode = True


class TimetableUpdate(BaseModel):
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    day_of_week: Optional[int] = None
    period: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    academic_year_id: Optional[int] = None


class NotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str]
    reference_id: Optional[int]
    is_read: bool
    created_on: datetime

    class Config:
        orm_mode = True


class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource: Optional[str]
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    created_on: datetime

    class Config:
        orm_mode = True


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
