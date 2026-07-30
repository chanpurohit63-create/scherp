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
    school_id: Optional[int] = None

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
    school_id: Optional[int] = None


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


# ========== SCHOOL (Multi-Tenant) ==========

class SchoolCreate(BaseModel):
    school_name: str
    school_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    subscription_plan: Optional[str] = "free"
    timezone: Optional[str] = "UTC"
    currency: Optional[str] = "USD"
    student_limit: Optional[int] = 0
    teacher_limit: Optional[int] = 0


class SchoolUpdate(BaseModel):
    school_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    status: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    student_limit: Optional[int] = None
    teacher_limit: Optional[int] = None
    logo: Optional[str] = None


class SchoolRead(BaseModel):
    id: int
    school_name: str
    school_code: str
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
    subscription_plan: Optional[str] = None
    subscription_start: Optional[date] = None
    subscription_end: Optional[date] = None
    status: str = "active"
    timezone: Optional[str] = "UTC"
    currency: Optional[str] = "USD"
    student_limit: Optional[int] = 0
    teacher_limit: Optional[int] = 0
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SchoolDashboardRead(BaseModel):
    total_students: int = 0
    total_teachers: int = 0
    total_parents: int = 0
    total_classes: int = 0
    total_subjects: int = 0
    active_enrollments: int = 0
    fee_collection: float = 0
    pending_fees: int = 0


class PlatformAnalyticsRead(BaseModel):
    total_schools: int = 0
    active_schools: int = 0
    suspended_schools: int = 0
    expired_schools: int = 0
    total_students: int = 0
    total_teachers: int = 0
    total_revenue: float = 0
    schools: List[SchoolRead] = []


class ParentCreate(BaseModel):
    user_id: int
    phone: Optional[str] = None
    address: Optional[str] = None


class ParentRead(BaseModel):
    id: int
    user_id: int
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        orm_mode = True


class ParentProfileRead(ParentRead):
    email: EmailStr
    full_name: Optional[str] = None
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
    employee_no: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: bool = True

    class Config:
        orm_mode = True


class TeacherProfileRead(TeacherRead):
    email: EmailStr
    full_name: Optional[str] = None
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
    admission_no: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    admission_date: Optional[date] = None
    status: str = "active"
    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    photo_path: Optional[str] = None

    class Config:
        orm_mode = True


class StudentProfileRead(StudentRead):
    email: EmailStr
    full_name: Optional[str] = None
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
    is_active: bool = False

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
    grade_level: Optional[str] = None

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
    code: Optional[str] = None

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
    section_id: Optional[int] = None

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
    section_id: Optional[int] = None
    enrolled_on: Optional[datetime] = None

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
    status: str = "present"
    remarks: Optional[str] = None

    class Config:
        orm_mode = True


class AttendanceUpdate(BaseModel):
    date: Optional[date] = None # type: ignore
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
    description: Optional[str] = None
    assigned_by: int
    class_id: int
    section_id: Optional[int] = None
    due_date: Optional[date] = None
    attachment_path: Optional[str] = None

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
    submitted_on: Optional[datetime] = None
    attachment_path: Optional[str] = None
    remarks: Optional[str] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None
    status: str = "submitted"

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
    status: str = "present"
    remarks: Optional[str] = None

    class Config:
        orm_mode = True


class TeacherAttendanceUpdate(BaseModel):
    date: Optional[date] = None # pyright: ignore[reportInvalidTypeForm]
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
    start_date: Optional[date] = None
    end_date: Optional[date] = None

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
    marks_obtained: Optional[float] = None
    max_marks: Optional[float] = None

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
    category: Optional[str] = None

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
    due_date: Optional[date] = None
    is_paid: bool = False

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
    paid_on: Optional[datetime] = None
    reference: Optional[str] = None

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
    content: Optional[str] = None
    target_roles: Optional[str] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    attachments_path: Optional[str] = None

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
    body: Optional[str] = None
    sender_id: int
    recipient_id: int
    sent_on: Optional[datetime] = None
    is_read: bool = False

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
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    event_type: Optional[str] = None
    target_roles: Optional[str] = None

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
    issue_date: Optional[datetime] = None
    remarks: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        orm_mode = True


class CertificateUpdate(BaseModel):
    certificate_type: Optional[str] = None
    issue_date: Optional[datetime] = None
    remarks: Optional[str] = None
    file_path: Optional[str] = None


class SchoolSettingsRead(BaseModel):
    id: int
    school_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_path: Optional[str] = None
    academic_year_id: Optional[int] = None

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
    total_students: int = 0
    total_teachers: int = 0
    attendance_percentage: float = 0
    fee_collection: float = 0
    pending_fees: int = 0
    upcoming_exams: int = 0
    upcoming_events: int = 0
    notices: List[NoticeRead] = []
    monthly_attendance: List[dict] = []
    monthly_fee_collection: List[dict] = []
    student_growth: List[dict] = []
    exam_performance: List[dict] = []


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
    uploaded_on: Optional[datetime] = None

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
    section_id: Optional[int] = None
    subject_id: int
    teacher_id: int
    day_of_week: int
    period: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
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


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    role: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = "normal"
    related_module: Optional[str] = None
    related_record_id: Optional[int] = None
    sender_id: Optional[int] = None
    school_id: Optional[int] = None
    notification_type: Optional[str] = "individual"
    action_url: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    expires_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None


class NotificationRead(BaseModel):
    id: int
    school_id: Optional[int] = None
    user_id: int
    role: Optional[str] = None
    notification_type: Optional[str] = None
    category: Optional[str] = None
    title: str
    message: str
    priority: Optional[str] = None
    related_module: Optional[str] = None
    related_record_id: Optional[int] = None
    action_url: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sender_id: Optional[int] = None
    is_read: bool = False
    is_archived: bool = False
    is_deleted: bool = False
    is_pinned: bool = False
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class BroadcastCreate(BaseModel):
    title: str
    message: str
    category: Optional[str] = None
    priority: Optional[str] = "normal"
    target_roles: Optional[str] = None
    target_class_id: Optional[int] = None
    target_section_id: Optional[int] = None
    target_user_ids: Optional[List[int]] = None
    action_url: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    expires_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None


class NotificationPreferenceCreate(BaseModel):
    email_enabled: Optional[bool] = True
    in_app_enabled: Optional[bool] = True
    sound_enabled: Optional[bool] = True
    browser_enabled: Optional[bool] = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationPreferenceRead(BaseModel):
    id: int
    user_id: int
    email_enabled: bool = True
    in_app_enabled: bool = True
    sound_enabled: bool = True
    browser_enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    class Config:
        orm_mode = True


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    browser_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


# ========== PASSWORD CHANGE ==========

class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# ========== AUDIT LOG ==========

class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    school_id: Optional[int] = None
    action: str
    resource: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    before_values: Optional[str] = None
    after_values: Optional[str] = None
    ip_address: Optional[str] = None
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class AuditLogCreate(BaseModel):
    action: str
    resource: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    before_values: Optional[str] = None
    after_values: Optional[str] = None


# ========== SUBSCRIPTION PLANS ==========

class SubscriptionPlan(BaseModel):
    name: str
    max_students: int
    max_teachers: int
    storage_mb: int
    modules: List[str] = []
    price_monthly: float = 0
    price_yearly: float = 0


SUBSCRIPTION_PLANS = {
    "free": SubscriptionPlan(name="Free", max_students=50, max_teachers=5, storage_mb=100, modules=["students", "attendance", "homework"], price_monthly=0, price_yearly=0),
    "basic": SubscriptionPlan(name="Basic", max_students=200, max_teachers=20, storage_mb=500, modules=["students", "attendance", "homework", "fees", "exams"], price_monthly=29, price_yearly=290),
    "standard": SubscriptionPlan(name="Standard", max_students=500, max_teachers=50, storage_mb=2000, modules=["students", "attendance", "homework", "fees", "exams", "transport", "library"], price_monthly=79, price_yearly=790),
    "premium": SubscriptionPlan(name="Premium", max_students=2000, max_teachers=200, storage_mb=10000, modules=["students", "attendance", "homework", "fees", "exams", "transport", "library", "hostel", "hr"], price_monthly=199, price_yearly=1990),
    "enterprise": SubscriptionPlan(name="Enterprise", max_students=10000, max_teachers=1000, storage_mb=50000, modules=["*"], price_monthly=499, price_yearly=4990),
}


# ========== PLATFORM DASHBOARD ==========

class PlatformDashboardRead(BaseModel):
    total_schools: int = 0
    active_schools: int = 0
    inactive_schools: int = 0
    suspended_schools: int = 0
    expired_schools: int = 0
    total_students: int = 0
    total_teachers: int = 0
    total_parents: int = 0
    total_staff: int = 0
    total_revenue: float = 0
    monthly_revenue: float = 0
    new_schools_this_month: int = 0
    active_users_today: int = 0
    subscription_distribution: List[dict] = []
    school_growth: List[dict] = []
    revenue_trend: List[dict] = []
    monthly_registrations: List[dict] = []


class SchoolStatisticsRead(BaseModel):
    school_id: int
    school_name: str
    total_students: int = 0
    total_teachers: int = 0
    total_parents: int = 0
    total_classes: int = 0
    total_revenue: float = 0
    subscription_plan: Optional[str] = None
    status: str = "active"


# ========== PERIOD MASTER ==========

class PeriodMasterCreate(BaseModel):
    period_name: str
    period_number: int
    start_time: str
    end_time: str
    is_break: Optional[bool] = False
    is_assembly: Optional[bool] = False
    is_sports: Optional[bool] = False
    is_library: Optional[bool] = False
    is_practical: Optional[bool] = False
    sort_order: Optional[int] = 0


class PeriodMasterRead(BaseModel):
    id: int
    period_name: str
    period_number: int
    start_time: str
    end_time: str
    is_break: bool
    is_assembly: bool
    is_sports: bool
    is_library: bool
    is_practical: bool
    sort_order: int
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PeriodMasterUpdate(BaseModel):
    period_name: Optional[str] = None
    period_number: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_break: Optional[bool] = None
    is_assembly: Optional[bool] = None
    is_sports: Optional[bool] = None
    is_library: Optional[bool] = None
    is_practical: Optional[bool] = None
    sort_order: Optional[int] = None


# ========== TEACHER AVAILABILITY ==========

class TeacherAvailabilityCreate(BaseModel):
    teacher_id: int
    day_of_week: int
    period_number: int
    is_available: bool = True
    availability_type: Optional[str] = "available"


class TeacherAvailabilityRead(BaseModel):
    id: int
    teacher_id: int
    day_of_week: int
    period_number: int
    is_available: bool
    availability_type: str
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TeacherAvailabilityUpdate(BaseModel):
    is_available: Optional[bool] = None
    availability_type: Optional[str] = None


# ========== TIMETABLE GENERATOR LOG ==========

class TimetableGeneratorLogRead(BaseModel):
    id: int
    academic_year_id: int
    generated_by: Optional[int] = None
    generation_type: str
    source_academic_year_id: Optional[int] = None
    source_section_id: Optional[int] = None
    config: Optional[str] = None
    result_summary: Optional[str] = None
    conflicts_found: int = 0
    conflicts_resolved: int = 0
    status: str
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


# ========== TIMETABLE CONFLICT LOG ==========

class TimetableConflictLogRead(BaseModel):
    id: int
    conflict_type: str
    conflict_description: str
    day_of_week: int
    period_number: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    room_id: Optional[int] = None
    subject_id: Optional[int] = None
    conflicting_record_id: Optional[int] = None
    resolved: bool = False
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


# ========== TIMETABLE DASHBOARD ==========

class TimetableDashboardRead(BaseModel):
    total_classes: int = 0
    total_teachers: int = 0
    today_classes: int = 0
    running_classes: int = 0
    free_rooms: int = 0
    occupied_rooms: int = 0
    teacher_utilization: float = 0.0
    room_utilization: float = 0.0
    avg_teaching_hours: float = 0.0
    upcoming_classes: List[dict] = []

    class Config:
        orm_mode = True


# ========== TIMETABLE GENERATION REQUEST ==========

class TimetableGenerateRequest(BaseModel):
    academic_year_id: int
    working_days: List[int] = [0, 1, 2, 3, 4, 5]
    school_start_time: str = "08:00"
    school_end_time: str = "15:00"
    periods_per_day: int = 6
    break_periods: List[int] = []
    max_periods_per_day: Optional[int] = None
    max_periods_per_week: Optional[int] = None
    auto_assign_teachers: bool = True
    auto_assign_rooms: bool = True
    auto_assign_periods: bool = True
    copy_from_academic_year_id: Optional[int] = None
    copy_from_section_id: Optional[int] = None
    copy_to_section_id: Optional[int] = None


# ========== TIMETABLE CONFLICT CHECK ==========

class TimetableConflictCheck(BaseModel):
    day_of_week: int
    period: int
    start_time: str
    end_time: str
    teacher_id: int
    class_id: int
    section_id: Optional[int] = None
    room_id: Optional[int] = None
    subject_id: Optional[int] = None
    exclude_timetable_id: Optional[int] = None


class TimetableConflictResult(BaseModel):
    has_conflict: bool
    conflicts: List[dict] = []
    messages: List[str] = []
    status: Optional[str] = None
    remarks: Optional[str] = None


# ========== PERIOD MASTER ==========

class PeriodMasterCreate(BaseModel):
    period_name: str
    period_number: int
    start_time: str
    end_time: str
    is_break: Optional[bool] = False
    is_assembly: Optional[bool] = False
    is_sports: Optional[bool] = False
    is_library: Optional[bool] = False
    is_practical: Optional[bool] = False
    sort_order: Optional[int] = 0


class PeriodMasterRead(BaseModel):
    id: int
    period_name: str
    period_number: int
    start_time: str
    end_time: str
    is_break: bool
    is_assembly: bool
    is_sports: bool
    is_library: bool
    is_practical: bool
    sort_order: int
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PeriodMasterUpdate(BaseModel):
    period_name: Optional[str] = None
    period_number: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_break: Optional[bool] = None
    is_assembly: Optional[bool] = None
    is_sports: Optional[bool] = None
    is_library: Optional[bool] = None
    is_practical: Optional[bool] = None
    sort_order: Optional[int] = None


# ========== TEACHER AVAILABILITY ==========

class TeacherAvailabilityCreate(BaseModel):
    teacher_id: int
    day_of_week: int
    period_number: int
    is_available: bool = True
    availability_type: Optional[str] = "available"


class TeacherAvailabilityRead(BaseModel):
    id: int
    teacher_id: int
    day_of_week: int
    period_number: int
    is_available: bool
    availability_type: str
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TeacherAvailabilityUpdate(BaseModel):
    is_available: Optional[bool] = None
    availability_type: Optional[str] = None


# ========== TIMETABLE GENERATOR LOG ==========

class TimetableGeneratorLogRead(BaseModel):
    id: int
    academic_year_id: int
    generated_by: Optional[int] = None
    generation_type: str
    source_academic_year_id: Optional[int] = None
    source_section_id: Optional[int] = None
    config: Optional[str] = None
    result_summary: Optional[str] = None
    conflicts_found: int = 0
    conflicts_resolved: int = 0
    status: str
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


# ========== TIMETABLE CONFLICT LOG ==========

class TimetableConflictLogRead(BaseModel):
    id: int
    conflict_type: str
    conflict_description: str
    day_of_week: int
    period_number: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    room_id: Optional[int] = None
    subject_id: Optional[int] = None
    conflicting_record_id: Optional[int] = None
    resolved: bool = False
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


# ========== TIMETABLE DASHBOARD ==========

class TimetableDashboardRead(BaseModel):
    total_classes: int = 0
    total_teachers: int = 0
    today_classes: int = 0
    running_classes: int = 0
    free_rooms: int = 0
    occupied_rooms: int = 0
    teacher_utilization: float = 0.0
    room_utilization: float = 0.0
    avg_teaching_hours: float = 0.0
    upcoming_classes: List[dict] = []

    class Config:
        orm_mode = True


# ========== TIMETABLE GENERATION REQUEST ==========

class TimetableGenerateRequest(BaseModel):
    academic_year_id: int
    working_days: List[int] = [0, 1, 2, 3, 4, 5]
    school_start_time: str = "08:00"
    school_end_time: str = "15:00"
    periods_per_day: int = 6
    break_periods: List[int] = []
    max_periods_per_day: Optional[int] = None
    max_periods_per_week: Optional[int] = None
    auto_assign_teachers: bool = True
    auto_assign_rooms: bool = True
    auto_assign_periods: bool = True
    copy_from_academic_year_id: Optional[int] = None
    copy_from_section_id: Optional[int] = None
    copy_to_section_id: Optional[int] = None


# ========== TIMETABLE CONFLICT CHECK ==========

class TimetableConflictCheck(BaseModel):
    day_of_week: int
    period: int
    start_time: str
    end_time: str
    teacher_id: int
    class_id: int
    section_id: Optional[int] = None
    room_id: Optional[int] = None
    subject_id: Optional[int] = None
    exclude_timetable_id: Optional[int] = None


class TimetableConflictResult(BaseModel):
    has_conflict: bool
    conflicts: List[dict] = []
    messages: List[str] = []
    status: Optional[str] = None
    remarks: Optional[str] = None


# ========== REPORT CARD TEMPLATES ==========

class ReportCardTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: Optional[str] = "standard"
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    exam_id: Optional[int] = None
    is_default: Optional[bool] = False
    config: Optional[str] = None
    header_config: Optional[str] = None
    footer_config: Optional[str] = None
    body_config: Optional[str] = None
    css_config: Optional[str] = None


class ReportCardTemplateRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    template_type: str
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    exam_id: Optional[int] = None
    is_default: bool
    is_archived: bool
    version: int
    parent_template_id: Optional[int] = None
    config: Optional[str] = None
    header_config: Optional[str] = None
    footer_config: Optional[str] = None
    body_config: Optional[str] = None
    css_config: Optional[str] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportCardTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    exam_id: Optional[int] = None
    is_default: Optional[bool] = None
    is_archived: Optional[bool] = None
    config: Optional[str] = None
    header_config: Optional[str] = None
    footer_config: Optional[str] = None
    body_config: Optional[str] = None
    css_config: Optional[str] = None


class ReportCardTemplateVersionRead(BaseModel):
    id: int
    template_id: int
    version: int
    config: Optional[str] = None
    header_config: Optional[str] = None
    footer_config: Optional[str] = None
    body_config: Optional[str] = None
    css_config: Optional[str] = None
    change_description: Optional[str] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportCardComponentCreate(BaseModel):
    template_id: int
    component_type: str
    label: str
    x_position: Optional[float] = 0.0
    y_position: Optional[float] = 0.0
    width: Optional[float] = 100.0
    height: Optional[float] = 50.0
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
    is_visible: Optional[bool] = True
    is_editable: Optional[bool] = True
    data_source: Optional[str] = None
    default_value: Optional[str] = None
    sort_order: Optional[int] = 0


class ReportCardComponentRead(BaseModel):
    id: int
    template_id: int
    component_type: str
    label: str
    x_position: float
    y_position: float
    width: float
    height: float
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
    is_visible: bool
    is_editable: bool
    data_source: Optional[str] = None
    default_value: Optional[str] = None
    sort_order: int
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportCardComponentUpdate(BaseModel):
    x_position: Optional[float] = None
    y_position: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
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
    is_visible: Optional[bool] = None
    is_editable: Optional[bool] = None
    data_source: Optional[str] = None
    default_value: Optional[str] = None
    sort_order: Optional[int] = None


# ========== EXAMINATION TYPES ==========

class ExaminationTypeCreate(BaseModel):
    name: str
    code: Optional[str] = None
    exam_type: Optional[str] = "theory"
    weightage: Optional[float] = 0.0
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None
    duration_minutes: Optional[int] = None
    show_in_report_card: Optional[bool] = True
    sort_order: Optional[int] = 0


class ExaminationTypeRead(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    exam_type: str
    weightage: float
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: bool
    is_published: bool
    show_in_report_card: bool
    sort_order: int
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ExaminationTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    exam_type: Optional[str] = None
    weightage: Optional[float] = None
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    show_in_report_card: Optional[bool] = None
    sort_order: Optional[int] = None


class ExamWeightageConfigCreate(BaseModel):
    academic_year_id: int
    class_id: int
    exam_type_id: int
    weightage: float = 0.0
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None


class ExamWeightageConfigRead(BaseModel):
    id: int
    academic_year_id: int
    class_id: int
    exam_type_id: int
    weightage: float
    max_marks: Optional[float] = None
    passing_marks: Optional[float] = None
    is_active: bool
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


# ========== GRADE ENGINE ==========

class GradeScaleCreate(BaseModel):
    name: str
    scale_type: Optional[str] = "percentage"
    min_value: Optional[float] = 0.0
    max_value: Optional[float] = 100.0
    passing_value: Optional[float] = 40.0
    is_default: Optional[bool] = False


class GradeScaleRead(BaseModel):
    id: int
    name: str
    scale_type: str
    min_value: float
    max_value: float
    passing_value: float
    is_default: bool
    is_active: bool
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class GradeScaleUpdate(BaseModel):
    name: Optional[str] = None
    scale_type: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    passing_value: Optional[float] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class GradeScaleRangeCreate(BaseModel):
    grade_scale_id: int
    grade: str
    grade_point: Optional[float] = None
    min_mark: float
    max_mark: float
    description: Optional[str] = None
    is_passing: Optional[bool] = True
    sort_order: Optional[int] = 0


class GradeScaleRangeRead(BaseModel):
    id: int
    grade_scale_id: int
    grade: str
    grade_point: Optional[float] = None
    min_mark: float
    max_mark: float
    description: Optional[str] = None
    is_passing: bool
    sort_order: int

    class Config:
        orm_mode = True


class GradeScaleRangeUpdate(BaseModel):
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    min_mark: Optional[float] = None
    max_mark: Optional[float] = None
    description: Optional[str] = None
    is_passing: Optional[bool] = None
    sort_order: Optional[int] = None


# ========== GPA ENGINE ==========

class GpaEngineConfigCreate(BaseModel):
    name: str
    scale_type: Optional[str] = "4_point"
    max_gpa: Optional[float] = 4.0
    min_gpa: Optional[float] = 0.0
    grade_point_decimals: Optional[int] = 2
    credit_based: Optional[bool] = False
    weighted: Optional[bool] = False
    formula_config: Optional[str] = None


class GpaEngineConfigRead(BaseModel):
    id: int
    name: str
    scale_type: str
    max_gpa: float
    min_gpa: float
    grade_point_decimals: int
    credit_based: bool
    weighted: bool
    formula_config: Optional[str] = None
    is_active: bool
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class GpaEngineConfigUpdate(BaseModel):
    name: Optional[str] = None
    scale_type: Optional[str] = None
    max_gpa: Optional[float] = None
    min_gpa: Optional[float] = None
    grade_point_decimals: Optional[int] = None
    credit_based: Optional[bool] = None
    weighted: Optional[bool] = None
    formula_config: Optional[str] = None
    is_active: Optional[bool] = None


# ========== GPA GRADE MAPPINGS ==========

class GpaGradeMappingCreate(BaseModel):
    gpa_engine_id: int
    grade: str
    grade_point: float
    min_percentage: float
    max_percentage: float
    description: Optional[str] = None
    is_passing: Optional[bool] = True
    sort_order: Optional[int] = 0


class GpaGradeMappingRead(BaseModel):
    id: int
    gpa_engine_id: int
    grade: str
    grade_point: float
    min_percentage: float
    max_percentage: float
    description: Optional[str] = None
    is_passing: bool
    sort_order: int

    class Config:
        orm_mode = True


class GpaGradeMappingUpdate(BaseModel):
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    min_percentage: Optional[float] = None
    max_percentage: Optional[float] = None
    description: Optional[str] = None
    is_passing: Optional[bool] = None
    sort_order: Optional[int] = None


# ========== SUBJECT CATEGORIES ==========

class SubjectCategoryCreate(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = 0


class SubjectCategoryRead(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    sort_order: int
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class SubjectCategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class SubjectCategoryMappingCreate(BaseModel):
    subject_id: int
    category_id: int
    is_primary: Optional[bool] = True


class SubjectCategoryMappingRead(BaseModel):
    id: int
    subject_id: int
    category_id: int
    is_primary: bool
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


# ========== REPORT CARDS ==========

class ReportCardCreate(BaseModel):
    academic_year_id: int
    exam_id: Optional[int] = None
    template_id: Optional[int] = None
    student_id: int
    class_id: int
    section_id: Optional[int] = None
    template_config: Optional[str] = None
    student_data: Optional[str] = None
    grades_data: Optional[str] = None
    overall_grade: Optional[str] = None
    overall_gpa: Optional[float] = None
    overall_percentage: Optional[float] = None
    total_marks_obtained: Optional[float] = None
    total_marks_possible: Optional[float] = None
    attendance_data: Optional[str] = None
    remarks: Optional[str] = None
    teacher_remark: Optional[str] = None
    principal_remark: Optional[str] = None


class ReportCardRead(BaseModel):
    id: int
    academic_year_id: int
    exam_id: Optional[int] = None
    template_id: Optional[int] = None
    student_id: int
    class_id: int
    section_id: Optional[int] = None
    overall_grade: Optional[str] = None
    overall_gpa: Optional[float] = None
    overall_percentage: Optional[float] = None
    total_marks_obtained: Optional[float] = None
    total_marks_possible: Optional[float] = None
    attendance_data: Optional[str] = None
    remarks: Optional[str] = None
    teacher_remark: Optional[str] = None
    principal_remark: Optional[str] = None
    status: str
    generated_by: Optional[int] = None
    generated_on: Optional[datetime] = None
    published_on: Optional[datetime] = None
    created_on: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportCardUpdate(BaseModel):
    academic_year_id: Optional[int] = None
    exam_id: Optional[int] = None
    template_id: Optional[int] = None
    student_id: Optional[int] = None
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    overall_grade: Optional[str] = None
    overall_gpa: Optional[float] = None
    overall_percentage: Optional[float] = None
    total_marks_obtained: Optional[float] = None
    total_marks_possible: Optional[float] = None
    attendance_data: Optional[str] = None
    remarks: Optional[str] = None
    teacher_remark: Optional[str] = None
    principal_remark: Optional[str] = None
    status: Optional[str] = None


class ReportCardSubjectCreate(BaseModel):
    report_card_id: int
    subject_id: int
    examination_type_id: Optional[int] = None
    marks_obtained: Optional[float] = None
    marks_max: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    grade_scale_range_id: Optional[int] = None
    remarks: Optional[str] = None
    teacher_remark: Optional[str] = None
    is_passing: Optional[bool] = None
    credit_hours: Optional[float] = None
    weightage: Optional[float] = None


class ReportCardSubjectRead(BaseModel):
    id: int
    report_card_id: int
    subject_id: int
    examination_type_id: Optional[int] = None
    marks_obtained: Optional[float] = None
    marks_max: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    grade_scale_range_id: Optional[int] = None
    remarks: Optional[str] = None
    teacher_remark: Optional[str] = None
    is_passing: Optional[bool] = None
    credit_hours: Optional[float] = None
    weightage: Optional[float] = None
    created_on: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportCardSubjectUpdate(BaseModel):
    marks_obtained: Optional[float] = None
    marks_max: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    grade_scale_range_id: Optional[int] = None
    remarks: Optional[str] = None
    teacher_remark: Optional[str] = None
    is_passing: Optional[bool] = None
    credit_hours: Optional[float] = None
    weightage: Optional[float] = None


# ========== BULK REPORT CARD GENERATION ==========

class BulkReportCardGenerate(BaseModel):
    academic_year_id: int
    exam_id: Optional[int] = None
    class_id: Optional[int] = None
    template_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    publish: Optional[bool] = False


class BulkReportCardResult(BaseModel):
    generated: int
    failed: int
    published: int
    errors: List[str] = []
