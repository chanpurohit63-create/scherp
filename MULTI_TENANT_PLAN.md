# Multi-Tenant Architecture Implementation Plan

## Overview
Convert single-school ERP into multi-tenant platform with complete data isolation.

## Phase 1: Database Models

### New School Model
```sql
schools
- id (PK)
- school_name
- school_code (unique)
- email, phone, address, city, state, country, postal_code
- logo, website, principal_name
- subscription_plan, subscription_start, subscription_end
- status (active, suspended, expired)
- timezone, currency
- student_limit, teacher_limit
- created_at, updated_at
```

### Add school_id to ALL tables:
User, Student, Teacher, Parent, AcademicYear, SchoolClass, Section, Subject, SubjectAllocation, Enrollment, Attendance, Homework, HomeworkSubmission, TeacherAttendance, Exam, ExamResult, FeeStructure, FeeAssignment, Payment, Notice, Message, Event, Certificate, Document, Timetable, Notification, NotificationPreference, DeviceToken, NotificationAuditLog, AuditLog

### Replace SchoolSettings with School model
SchoolSettings becomes redundant — School model replaces it.

## Phase 2: Authentication

### JWT Changes
Token payload: `{ sub: email, role, school_id, user_id }`

### New Dependencies
- `get_current_school(current_user)` — returns school_id
- `require_school_admin` — Super Admin or School Admin of that school

### Security Rule
NEVER trust `school_id` from frontend. Always derive from authenticated user JWT.

## Phase 3: Backend CRUD & Routers

### Generic CRUD Updates
All crud functions need `school_id` parameter:
- `list_items(model, school_id, ...)` adds `.where(model.school_id == school_id)`
- `create_item(item)` — item already has school_id set
- `get_item(model, id, school_id)` — verify ownership

### Super Admin Router (NEW)
- POST/DELETE/PUT /api/schools
- GET /api/schools (list all)
- GET /api/schools/{id}/dashboard
- POST /api/schools/{id}/suspend/activate
- GET /api/platform/dashboard
- GET /api/platform/analytics

### ERP Router Changes (Massive)
Every single endpoint in erp.py needs:
```python
school_id = current_user.school_id
```
Added to every query:
```python
.where(model.school_id == school_id)
```

### Seed Script Update
Create default school + Super Admin on first run.

## Phase 4: Frontend Changes

### useAuth Hook
- Store `school_id` in token/profile
- Expose `schoolId`, `isSuperAdmin`

### Navigation
- Super Admin sees "Platform Dashboard" + all schools
- School Admin sees scoped view of their school
- Student/Parent/Teacher see only their school's data

### API Layer
No changes needed — school_id is in JWT, backend filters automatically.

## Files to Modify

### Backend (10 files)
1. `backend/app/models.py` — Add School model, school_id to all tables
2. `backend/app/schemas.py` — School CRUD schemas
3. `backend/app/auth.py` — JWT includes school_id, new dependencies
4. `backend/app/crud.py` — school-scoped generic functions
5. `backend/app/main.py` — Super Admin router registration, seed school
6. `backend/app/routers/erp.py` — school_id filter on ALL queries
7. `backend/app/routers/users.py` — school_id filter
8. `backend/app/routers/notifications.py` — school_id in WS + queries
9. `backend/app/notification_service.py` — school_id in notifications
10. `backend/seed.py` — Create default school + Super Admin

### Frontend (2 files)
1. `frontend/src/hooks/useAuth.jsx` — school_id in context
2. `frontend/src/App.jsx` — Super Admin routes

## Risk Assessment
- HIGH: Every ERP router endpoint must be updated (200+ endpoints)
- MEDIUM: Existing dev.db must be deleted, all data recreated
- LOW: Frontend changes are minimal — school_id handled server-side

## Order of Implementation
1. Models (School + school_id on all tables)
2. Auth (JWT school_id)
3. CRUD (school-scoped generics)
4. Super Admin router
5. ERP router (bulk update all endpoints)
6. Users router
7. Notifications
8. Seed script
9. Frontend
</｜｜DSML｜｜parameter>
</｜｜DSML｜｜invoke>
</｜｜DSML｜｜tool_calls>
