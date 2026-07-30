# Phase 3: Enterprise Timetable Management System

## Steps

### Step 1: Database Models
- [ ] Add `Room` model to `backend/app/models.py`
- [ ] Upgrade `Timetable` model with new fields (room_id, status, remarks, created_by, updated_by, created_at, updated_at)

### Step 2: Pydantic Schemas
- [ ] Add Room schemas (Create, Read, Update) to `backend/app/schemas.py`
- [ ] Upgrade Timetable schemas with new fields

### Step 3: API Endpoints
- [ ] Add Room CRUD endpoints (POST/GET/PUT/DELETE) to `backend/app/routers/erp.py`
- [ ] Upgrade Timetable CRUD with enhanced conflict detection
- [ ] Add Teacher Timetable endpoint: `GET /portal/teacher/timetable`
- [ ] Add Student Timetable endpoint: `GET /portal/student/timetable`
- [ ] Add Class Timetable endpoint: `GET /timetable/class/{class_id}`
- [ ] Add Room Timetable endpoint: `GET /timetable/room/{room_id}`
- [ ] Add Printable Timetable: `GET /timetable/printable/{class_id}`
- [ ] Add Weekly/Daily Schedule endpoints

