"""
Full end-to-end ERP test - exercises every workflow like a real school.
Runs against the live REST API (same endpoints the React frontend calls).
"""
import requests
import json
import sys
import traceback
from datetime import date, datetime, timedelta

BASE = "http://127.0.0.1:8000"
results = []

def log(step, name, expected, actual, ok, err=None, root_cause=None, fix=None):
    results.append({
        "step": step, "name": name, "expected": expected, "actual": actual,
        "ok": ok, "error": err, "root_cause": root_cause, "fix": fix,
    })
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {step} | {name}")
    if not ok:
        print(f"    Expected: {expected}")
        print(f"    Actual: {actual}")
        if err: print(f"    Error: {err}")
        if root_cause: print(f"    Root Cause: {root_cause}")
        if fix: print(f"    Fix: {fix}")

def req(method, path, token=None, json_body=None, files=None):
    headers = {}
    if token: headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{path}", headers=headers, timeout=30)
        elif method == "POST":
            if files:
                r = requests.post(f"{BASE}{path}", headers=headers, files=files, timeout=60)
            else:
                r = requests.post(f"{BASE}{path}", headers=headers, json=json_body, timeout=30)
        elif method == "PUT":
            r = requests.put(f"{BASE}{path}", headers=headers, json=json_body, timeout=30)
        elif method == "DELETE":
            r = requests.delete(f"{BASE}{path}", headers=headers, timeout=30)
        else:
            return None, None, "Unsupported method"
        try:
            body = r.json()
        except Exception:
            body = r.text
        return r.status_code, body, None
    except Exception as e:
        return None, None, str(e)

def login(email, password):
    r = requests.post(f"{BASE}/auth/token", data={"username": email, "password": password}, timeout=30)
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

# =====================================================================
# STEP 2 - SCHOOL ADMIN
# =====================================================================
print("=" * 80)
print("STEP 2 - SCHOOL ADMIN")
print("=" * 80)

# Get school_id from the school created in step 1
school_id = 2  # School created in step 1

# Login as the school admin created in step 1
admin_token = login("schooladmin@testalpha.edu", "AdminPass123!")
log("2.1", "School Admin login", "Token returned", f"Token {'returned' if admin_token else 'FAILED'}", admin_token is not None,
    err="Login failed" if not admin_token else None)

if admin_token:
    # 2.2 Force password change (change password)
    status, body, err = req("POST", "/api/profile/change-password?old_password=AdminPass123!&new_password=NewAdminPass456!", admin_token)
    log("2.2", "Force password change", "200 + success", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    # Re-login with new password
    admin_token = login("schooladmin@testalpha.edu", "NewAdminPass456!")
    log("2.3", "Login with new password", "Token returned", f"Token {'returned' if admin_token else 'FAILED'}", admin_token is not None,
        err="Login with new password failed" if not admin_token else None)

    # 2.4 Setup wizard - school settings
    status, body, err = req("GET", "/api/settings", admin_token)
    log("2.4", "Setup wizard - get settings", "200 + settings", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    status, body, err = req("PUT", "/api/settings", admin_token, {
        "school_name": "Test School Alpha",
        "address": "123 Test St, Springfield",
        "phone": "555-1234",
        "email": "info@testalpha.edu",
        "principal_name": "Dr. Principal",
        "theme_color": "#4f46e5",
    })
    log("2.5", "Setup wizard - save school settings", "200 + updated settings", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    # 2.6 Dashboard loads
    status, body, err = req("GET", "/api/dashboard/summary", admin_token)
    log("2.6", "School Admin dashboard loads", "200 + summary", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# STEP 3 - SCHOOL SETUP
# =====================================================================
print("=" * 80)
print("STEP 3 - SCHOOL SETUP")
print("=" * 80)

if admin_token:
    # 3.1 Academic Session
    status, body, err = req("POST", "/api/academic-years", admin_token, {
        "name": "2026-2027", "start_date": "2026-04-01", "end_date": "2027-03-31", "is_active": True
    })
    ay_ok = status == 201 and body.get("id")
    log("3.1", "Create academic session", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ay_ok,
        err=str(err) if err else (str(body) if not ay_ok else None))
    ay_id = body.get("id") if ay_ok else None

    # 3.2 Classes
    class_ids = {}
    for cls_name, grade in [("Class 4", "4"), ("Class 5", "5")]:
        status, body, err = req("POST", "/api/classes", admin_token, {"name": cls_name, "grade_level": grade})
        ok = status == 201 and body.get("id")
        log("3.2", f"Create {cls_name}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
            err=str(err) if err else (str(body) if not ok else None))
        if ok: class_ids[cls_name] = body["id"]

    # 3.3 Sections
    section_ids = {}
    for cls_name, cls_id in class_ids.items():
        for sec in ["A", "B"]:
            status, body, err = req("POST", "/api/sections", admin_token, {"name": sec, "class_id": cls_id})
            ok = status == 201 and body.get("id")
            log("3.3", f"Create section {cls_name}-{sec}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
                err=str(err) if err else (str(body) if not ok else None))
            if ok: section_ids[f"{cls_name}-{sec}"] = body["id"]

    # 3.4 Subjects
    subject_ids = {}
    for subj in [("Mathematics", "MATH"), ("English", "ENG"), ("Science", "SCI"), ("Hindi", "HIN")]:
        status, body, err = req("POST", "/api/subjects", admin_token, {"name": subj[0], "code": subj[1]})
        ok = status == 201 and body.get("id")
        log("3.4", f"Create subject {subj[0]}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
            err=str(err) if err else (str(body) if not ok else None))
        if ok: subject_ids[subj[0]] = body["id"]

    # 3.5 Fee Structure
    fee_ids = {}
    for fee in [("Tuition Fee", 5000.0, "Tuition"), ("Exam Fee", 1000.0, "Exam"), ("Transport Fee", 2000.0, "Transport")]:
        status, body, err = req("POST", "/api/fee-structures", admin_token, {"name": fee[0], "amount": fee[1], "category": fee[2]})
        ok = status == 201 and body.get("id")
        log("3.5", f"Create fee structure {fee[0]}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
            err=str(err) if err else (str(body) if not ok else None))
        if ok: fee_ids[fee[0]] = body["id"]

    # 3.6 Exam Types
    status, body, err = req("POST", "/api/examination-types", admin_token, {
        "name": "Mid Term", "code": "MID", "exam_type": "theory", "weightage": 50.0,
        "max_marks": 100, "passing_marks": 40, "is_active": True
    })
    exam_type_ok = status == 201 and body.get("id")
    log("3.6", "Create exam type", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", exam_type_ok,
        err=str(err) if err else (str(body) if not exam_type_ok else None))
    exam_type_id = body.get("id") if exam_type_ok else None

    # 3.7 Rooms (for timetable)
    status, body, err = req("POST", "/api/rooms", admin_token, {
        "room_name": "Room 101", "room_number": "101", "building": "Main", "capacity": 40, "room_type": "Classroom"
    })
    room_ok = status == 201 and body.get("id")
    log("3.7", "Create room", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", room_ok,
        err=str(err) if err else (str(body) if not room_ok else None))
    room_id = body.get("id") if room_ok else None

    # 3.8 Periods (for timetable)
    status, body, err = req("POST", "/api/periods", admin_token, {
        "period_name": "Period 1", "period_number": 1, "start_time": "08:00", "end_time": "08:45", "sort_order": 1
    })
    period_ok = status == 201 and body.get("id")
    log("3.8", "Create period", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", period_ok,
        err=str(err) if err else (str(body) if not period_ok else None))
    period_id = body.get("id") if period_ok else None

    # 3.9 Houses (via events or certificates - check if houses exist)
    # Houses are not a separate model - check if there's a house concept
    # For now, create an event as a house activity
    status, body, err = req("POST", "/api/events", admin_token, {
        "title": "House Sports Day", "description": "Annual sports day",
        "start_date": "2026-08-15T09:00:00", "end_date": "2026-08-15T17:00:00",
        "event_type": "sports", "target_roles": "all"
    })
    event_ok = status == 201 and body.get("id")
    log("3.9", "Create house event", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", event_ok,
        err=str(err) if err else (str(body) if not event_ok else None))

# =====================================================================
# STEP 4 - TEACHERS
# =====================================================================
print("=" * 80)
print("STEP 4 - TEACHERS")
print("=" * 80)

teacher_ids = {}
teacher_tokens = {}
if admin_token:
    # Create 2 teachers with login credentials
    for i, (name, email, emp_no) in enumerate([
        ("Ms. Sarah Wilson", "teacher1@testalpha.edu", "T001"),
        ("Mr. Robert Chen", "teacher2@testalpha.edu", "T002"),
    ]):
        # Register user
        status, body, err = req("POST", f"/auth/register?school_id={school_id}", None, {
            "email": email, "password": "TeacherPass123!", "full_name": name, "role": "Teacher"
        })
        user_ok = status == 200 and body.get("id")
        log("4.1", f"Create teacher user {name}", "200 + user id", f"{status} user_id={body.get('id') if isinstance(body, dict) else 'N/A'}", user_ok,
            err=str(err) if err else (str(body) if not user_ok else None))
        user_id = body.get("id") if user_ok else None

        # Create teacher profile
        status, body, err = req("POST", "/api/teachers", admin_token, {
            "user_id": user_id, "employee_no": emp_no, "hire_date": "2025-06-01", "is_active": True
        })
        teacher_ok = status == 201 and body.get("id")
        log("4.2", f"Create teacher profile {name}", "201 + teacher id", f"{status} teacher_id={body.get('id') if isinstance(body, dict) else 'N/A'}", teacher_ok,
            err=str(err) if err else (str(body) if not teacher_ok else None))
        if teacher_ok:
            teacher_ids[name] = body["id"]
            teacher_tokens[name] = login(email, "TeacherPass123!")

    # 4.3 Assign subjects to teachers
    if teacher_ids and subject_ids and class_ids:
        for tname, tid in teacher_ids.items():
            for subj_name, sid in subject_ids.items():
                for cls_name, cid in class_ids.items():
                    status, body, err = req("POST", "/api/subject-allocations", admin_token, {
                        "subject_id": sid, "teacher_id": tid, "class_id": cid
                    })
                    ok = status == 201 and body.get("id")
                    log("4.3", f"Assign {subj_name} to {tname} for {cls_name}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
                        err=str(err) if err else (str(body) if not ok else None))

    # 4.4 Login as each teacher and test features
    for tname, ttoken in teacher_tokens.items():
        if ttoken:
            status, body, err = req("GET", "/api/portal/teacher/dashboard", ttoken)
            log("4.4", f"Teacher {tname} dashboard", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

            status, body, err = req("GET", "/api/portal/teacher/classes", ttoken)
            log("4.4", f"Teacher {tname} classes", "200 + classes", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

            status, body, err = req("GET", "/api/portal/teacher/profile", ttoken)
            log("4.4", f"Teacher {tname} profile", "200 + profile", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

            status, body, err = req("GET", "/api/portal/teacher/calendar", ttoken)
            log("4.4", f"Teacher {tname} calendar", "200 + calendar", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

            status, body, err = req("GET", "/api/portal/teacher/messages", ttoken)
            log("4.4", f"Teacher {tname} messages", "200 + messages", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# STEP 5 - STUDENTS
# =====================================================================
print("=" * 80)
print("STEP 5 - STUDENTS")
print("=" * 80)

student_ids = {}
student_tokens = {}
if admin_token:
    # Create 5 students (3 in Class 4, 2 in Class 5)
    students = [
        ("Alice Anderson", "STU001", "Class 4", "2015-05-10", "F", "A+", "John Anderson", "555-1001", "john.anderson@email.com", "123 Main St", "123456789012"),
        ("Bob Barker", "STU002", "Class 4", "2015-08-22", "M", "B+", "Mary Barker", "555-1002", "mary.barker@email.com", "456 Oak St", "234567890123"),
        ("Carol Clark", "STU003", "Class 4", "2015-11-03", "F", "O+", "David Clark", "555-1003", "david.clark@email.com", "789 Pine St", "345678901234"),
        ("David Doe", "STU004", "Class 5", "2014-03-15", "M", "AB+", "Sarah Doe", "555-1004", "sarah.doe@email.com", "321 Elm St", "456789012345"),
        ("Eve Evans", "STU005", "Class 5", "2014-07-28", "F", "A-", "Robert Evans", "555-1005", "robert.evans@email.com", "654 Maple St", "567890123456"),
    ]
    for name, adm_no, cls, dob, gender, blood, parent_name, parent_phone, parent_email, address, aadhaar in students:
        # Register user
        email = f"student_{adm_no.lower()}@testalpha.edu"
        status, body, err = req("POST", f"/auth/register?school_id={school_id}", None, {
            "email": email, "password": "StudentPass123!", "full_name": name, "role": "Student"
        })
        user_ok = status == 200 and body.get("id")
        log("5.1", f"Create student user {name}", "200 + user id", f"{status} user_id={body.get('id') if isinstance(body, dict) else 'N/A'}", user_ok,
            err=str(err) if err else (str(body) if not user_ok else None))
        user_id = body.get("id") if user_ok else None

        # Create student profile
        status, body, err = req("POST", "/api/students", admin_token, {
            "user_id": user_id, "admission_no": adm_no, "dob": dob, "gender": gender,
            "admission_date": "2026-04-01", "status": "active"
        })
        student_ok = status == 201 and body.get("id")
        log("5.2", f"Create student profile {name}", "201 + student id", f"{status} student_id={body.get('id') if isinstance(body, dict) else 'N/A'}", student_ok,
            err=str(err) if err else (str(body) if not student_ok else None))
        if student_ok:
            student_ids[name] = body["id"]
            student_tokens[name] = login(email, "StudentPass123!")

    # 5.3 Enroll students in classes
    for name, adm_no, cls, *_ in students:
        if name in student_ids:
            cid = class_ids.get(cls)
            if cid:
                status, body, err = req("POST", "/api/enrollments", admin_token, {
                    "student_id": student_ids[name], "academic_year_id": ay_id, "class_id": cid
                })
                ok = status == 201 and body.get("id")
                log("5.3", f"Enroll {name} in {cls}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
                    err=str(err) if err else (str(body) if not ok else None))

    # 5.4 Login as each student and test portal
    for sname, stoken in student_tokens.items():
        if stoken:
            status, body, err = req("GET", "/api/portal/student/dashboard", stoken)
            log("5.4", f"Student {sname} dashboard", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))
            status, body, err = req("GET", "/api/portal/student/profile", stoken)
            log("5.4", f"Student {sname} profile", "200 + profile", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# STEP 6 - PARENTS
# =====================================================================
print("=" * 80)
print("STEP 6 - PARENTS")
print("=" * 80)

parent_ids = {}
parent_tokens = {}
if admin_token:
    # Create parent accounts and link to students
    for name, adm_no, cls, dob, gender, blood, parent_name, parent_phone, parent_email, address, aadhaar in students:
        # Register parent user
        status, body, err = req("POST", f"/auth/register?school_id={school_id}", None, {
            "email": parent_email, "password": "ParentPass123!", "full_name": parent_name, "role": "Parent"
        })
        user_ok = status == 200 and body.get("id")
        log("6.1", f"Create parent user {parent_name}", "200 + user id", f"{status} user_id={body.get('id') if isinstance(body, dict) else 'N/A'}", user_ok,
            err=str(err) if err else (str(body) if not user_ok else None))
        parent_user_id = body.get("id") if user_ok else None

        # Create parent profile
        status, body, err = req("POST", "/api/parents", admin_token, {
            "user_id": parent_user_id, "phone": parent_phone, "address": address
        })
        parent_ok = status == 201 and body.get("id")
        log("6.2", f"Create parent profile {parent_name}", "201 + parent id", f"{status} parent_id={body.get('id') if isinstance(body, dict) else 'N/A'}", parent_ok,
            err=str(err) if err else (str(body) if not parent_ok else None))
        if parent_ok:
            parent_ids[parent_name] = body["id"]
            parent_tokens[parent_name] = login(parent_email, "ParentPass123!")

            # Link parent to student (update student father_id)
            if name in student_ids:
                status, body, err = req("PUT", f"/api/students/{student_ids[name]}", admin_token, {"father_id": body["id"]})
                link_ok = status == 200
                log("6.3", f"Link {parent_name} to {name}", "200 + linked", f"{status}", link_ok,
                    err=str(err) if err else (str(body) if not link_ok else None))

    # 6.4 Login as each parent and verify child isolation
    for pname, ptoken in parent_tokens.items():
        if ptoken:
            status, body, err = req("GET", "/api/portal/parent/children", ptoken)
            children_ok = status == 200 and len(body) == 1
            log("6.4", f"Parent {pname} sees only own child", "1 child", f"{status} children={len(body) if isinstance(body, list) else 'err'}", children_ok,
                err=str(err) if err else (str(body) if not children_ok else None))

            status, body, err = req("GET", "/api/portal/parent/dashboard", ptoken)
            log("6.4", f"Parent {pname} dashboard", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

            # Verify parent cannot access another child
            if student_ids:
                # Find a student that is NOT this parent's child
                other_student = None
                for sname, sid in student_ids.items():
                    if sname not in [s[0] for s in students if s[6] == pname]:
                        other_student = sid
                        break
                if other_student:
                    status, body, err = req("GET", f"/api/portal/parent/children/{other_student}/profile", ptoken)
                    isolation_ok = status == 403
                    log("6.4", f"Parent {pname} blocked from other child", "403", f"{status}", isolation_ok,
                        err=str(err) if err else (str(body) if not isolation_ok else None))

# =====================================================================
# STEP 7 - ATTENDANCE
# =====================================================================
print("=" * 80)
print("STEP 7 - ATTENDANCE")
print("=" * 80)

attendance_ids = {}
if admin_token:
    today = date.today().isoformat()
    for sname, sid in student_ids.items():
        status, body, err = req("POST", "/api/attendances", admin_token, {
            "student_id": sid, "date": today, "status": "present", "remarks": "On time"
        })
        ok = status == 201 and body.get("id")
        log("7.1", f"Mark attendance for {sname}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
            err=str(err) if err else (str(body) if not ok else None))
        if ok: attendance_ids[sname] = body["id"]

    # 7.2 Edit attendance
    if attendance_ids:
        first = list(attendance_ids.values())[0]
        status, body, err = req("PUT", f"/api/attendances/{first}", admin_token, {"status": "absent", "remarks": "Sick"})
        edit_ok = status == 200 and body.get("status") == "absent"
        log("7.2", "Edit attendance", "200 + status=absent", f"{status} status={body.get('status') if isinstance(body, dict) else 'N/A'}", edit_ok,
            err=str(err) if err else (str(body) if not edit_ok else None))

    # 7.3 View reports
    status, body, err = req("GET", "/api/reports/attendance", admin_token)
    log("7.3", "Attendance report", "200 + data", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    # 7.4 Student portal shows attendance
    for sname, stoken in student_tokens.items():
        if stoken:
            status, body, err = req("GET", "/api/portal/student/attendance", stoken)
            log("7.4", f"Student {sname} sees attendance", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

    # 7.5 Parent portal shows attendance
    for pname, ptoken in parent_tokens.items():
        if ptoken and student_ids:
            # Find the child of this parent
            child_id = None
            for sname, sid in student_ids.items():
                if sname in [s[0] for s in students if s[6] == pname]:
                    child_id = sid
                    break
            if child_id:
                status, body, err = req("GET", f"/api/portal/parent/children/{child_id}/attendance", ptoken)
                log("7.5", f"Parent {pname} sees child attendance", "200 + data", f"{status}", status == 200,
                    err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# STEP 8 - HOMEWORK
# =====================================================================
print("=" * 80)
print("STEP 8 - HOMEWORK")
print("=" * 80)

homework_ids = {}
if teacher_tokens and student_ids:
    # Teacher creates homework
    tname = list(teacher_tokens.keys())[0]
    ttoken = teacher_tokens[tname]
    tid = teacher_ids[tname]
    cid = class_ids.get("Class 4")
    if cid:
        status, body, err = req("POST", "/api/portal/teacher/homework", ttoken, {
            "title": "Math Homework - Chapter 1",
            "description": "Solve problems 1-10 from Chapter 1",
            "assigned_by": tid, "class_id": cid, "due_date": (date.today() + timedelta(days=7)).isoformat()
        })
        hw_ok = status in (200, 201) and body.get("id")
        log("8.1", "Teacher creates homework", "200/201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", hw_ok,
            err=str(err) if err else (str(body) if not hw_ok else None))
        if hw_ok: homework_ids["math"] = body["id"]

    # Student views homework
    for sname, stoken in student_tokens.items():
        if stoken:
            status, body, err = req("GET", "/api/portal/student/homework", stoken)
            log("8.2", f"Student {sname} views homework", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

    # Parent views homework
    for pname, ptoken in parent_tokens.items():
        if ptoken and student_ids:
            child_id = None
            for sname, sid in student_ids.items():
                if sname in [s[0] for s in students if s[6] == pname]:
                    child_id = sid
                    break
            if child_id:
                status, body, err = req("GET", f"/api/portal/parent/children/{child_id}/homework", ptoken)
                log("8.3", f"Parent {pname} views child homework", "200 + data", f"{status}", status == 200,
                    err=str(err) if err else (str(body) if status != 200 else None))

    # Student submits homework
    if homework_ids:
        hw_id = homework_ids["math"]
        for sname, stoken in student_tokens.items():
            if stoken and sname in student_ids:
                status, body, err = req("POST", f"/api/portal/student/homework/{hw_id}/submit", stoken, {
                    "remarks": "Completed all problems"
                })
                ok = status == 200 or status == 201
                log("8.4", f"Student {sname} submits homework", "200/201", f"{status}", ok,
                    err=str(err) if err else (str(body) if not ok else None))

        # Teacher grades submission
        status, body, err = req("GET", f"/api/portal/teacher/homework/{hw_id}/submissions", ttoken)
        if status == 200 and isinstance(body, list) and body:
            sub = body[0]
            sub_id = sub.get("submission", sub).get("id", sub.get("id"))
            if sub_id:
                status, body, err = req("PUT", f"/api/portal/teacher/homework/{hw_id}/submissions/{sub_id}/grade?grade=A&feedback=Excellent", ttoken)
                grade_ok = status == 200
                log("8.5", "Teacher grades homework", "200 + graded", f"{status}", grade_ok,
                    err=str(err) if err else (str(body) if not grade_ok else None))
            else:
                log("8.5", "Teacher grades homework", "200 + graded", f"submission={body[0]}", False,
                    err="Could not extract submission id")
        else:
            log("8.5", "Teacher grades homework", "200 + graded", f"submissions={status} {body}", False,
                err="No submissions found to grade")

# =====================================================================
# STEP 9 - EXAMS
# =====================================================================
print("=" * 80)
print("STEP 9 - EXAMS")
print("=" * 80)

exam_id = None
if admin_token and ay_id:
    # Create exam
    status, body, err = req("POST", "/api/exams", admin_token, {
        "name": "Mid Term Exam 2026", "academic_year_id": ay_id,
        "start_date": "2026-08-01", "end_date": "2026-08-05"
    })
    exam_ok = status == 201 and body.get("id")
    log("9.1", "Create exam", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", exam_ok,
        err=str(err) if err else (str(body) if not exam_ok else None))
    exam_id = body.get("id") if exam_ok else None

    # Enter marks for every student
    if exam_id and student_ids and subject_ids:
        for sname, sid in student_ids.items():
            for subj_name, subj_id in subject_ids.items():
                marks = 85 if sname != "Bob Barker" else 45
                status, body, err = req("POST", "/api/exam-results", admin_token, {
                    "exam_id": exam_id, "student_id": sid, "subject_id": subj_id,
                    "marks_obtained": marks, "max_marks": 100
                })
                ok = status == 201 and body.get("id")
                log("9.2", f"Enter marks for {sname} in {subj_name}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
                    err=str(err) if err else (str(body) if not ok else None))

    # Generate results
    status, body, err = req("GET", "/api/reports/exams", admin_token)
    log("9.3", "Generate exam results report", "200 + data", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    # Generate report cards
    if exam_id and student_ids:
        for sname, sid in student_ids.items():
            status, body, err = req("POST", "/api/report-cards/generate", admin_token, {
                "student_id": sid, "exam_id": exam_id, "academic_year_id": ay_id
            })
            ok = status in (200, 201) and body.get("id")
            log("9.4", f"Generate report card for {sname}", "200/201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
                err=str(err) if err else (str(body) if not ok else None))

    # Publish report cards
    status, body, err = req("GET", "/api/report-cards", admin_token)
    if status == 200 and isinstance(body, list):
        for rc in body:
            status, body2, err = req("POST", f"/api/report-cards/{rc['id']}/publish", admin_token, {})
            ok = status == 200
            log("9.5", f"Publish report card {rc['id']}", "200 + published", f"{status}", ok,
                err=str(err) if err else (str(body2) if not ok else None))

    # Download PDF
    status, body, err = req("GET", "/api/report-cards", admin_token)
    if status == 200 and isinstance(body, list) and body:
        rc_id = body[0]["id"]
        status, body, err = req("GET", f"/api/report-cards/{rc_id}/pdf", admin_token)
        pdf_ok = status == 200
        log("9.6", "Download report card PDF", "200 + PDF", f"{status}", pdf_ok,
            err=str(err) if err else (str(body) if not pdf_ok else None))

    # Student portal shows report card
    for sname, stoken in student_tokens.items():
        if stoken:
            status, body, err = req("GET", "/api/portal/student/exams/report-card", stoken)
            log("9.7", f"Student {sname} sees report card", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

    # Parent portal shows report card
    for pname, ptoken in parent_tokens.items():
        if ptoken and student_ids:
            child_id = None
            for sname, sid in student_ids.items():
                if sname in [s[0] for s in students if s[6] == pname]:
                    child_id = sid
                    break
            if child_id:
                status, body, err = req("GET", f"/api/portal/parent/children/{child_id}/results", ptoken)
                log("9.8", f"Parent {pname} sees child results", "200 + data", f"{status}", status == 200,
                    err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# STEP 10 - FEES
# =====================================================================
print("=" * 80)
print("STEP 10 - FEES")
print("=" * 80)

if admin_token and fee_ids and student_ids:
    # Assign fee structures
    for sname, sid in student_ids.items():
        for fee_name, fid in fee_ids.items():
            status, body, err = req("POST", "/api/fee-assignments", admin_token, {
                "student_id": sid, "fee_structure_id": fid, "due_date": "2026-08-31", "is_paid": False
            })
            ok = status == 201 and body.get("id")
            log("10.1", f"Assign {fee_name} to {sname}", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", ok,
                err=str(err) if err else (str(body) if not ok else None))

    # Record payments
    status, body, err = req("GET", "/api/fee-assignments", admin_token)
    if status == 200 and isinstance(body, list) and body:
        for fa in body[:3]:
            status, body2, err = req("POST", "/api/payments", admin_token, {
                "fee_assignment_id": fa["id"], "amount": 5000.0, "reference": f"PAY-{fa['id']}"
            })
            ok = status == 201 and body2.get("id")
            log("10.2", f"Record payment for fee assignment {fa['id']}", "201 + id", f"{status} id={body2.get('id') if isinstance(body2, dict) else 'N/A'}", ok,
                err=str(err) if err else (str(body2) if not ok else None))

    # Verify balances
    status, body, err = req("GET", "/api/reports/fees", admin_token)
    log("10.3", "Fee report", "200 + data", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    # Student portal fees
    for sname, stoken in student_tokens.items():
        if stoken:
            status, body, err = req("GET", "/api/portal/student/fees", stoken)
            log("10.4", f"Student {sname} sees fees", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

    # Parent portal fees
    for pname, ptoken in parent_tokens.items():
        if ptoken and student_ids:
            child_id = None
            for sname, sid in student_ids.items():
                if sname in [s[0] for s in students if s[6] == pname]:
                    child_id = sid
                    break
            if child_id:
                status, body, err = req("GET", f"/api/portal/parent/children/{child_id}/fees", ptoken)
                log("10.5", f"Parent {pname} sees child fees", "200 + data", f"{status}", status == 200,
                    err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# STEP 11 - NOTIFICATIONS
# =====================================================================
print("=" * 80)
print("STEP 11 - NOTIFICATIONS")
print("=" * 80)

if admin_token:
    # Create notice
    status, body, err = req("POST", "/api/notices", admin_token, {
        "title": "School Holiday Notice",
        "content": "School will be closed on Aug 15 for Independence Day.",
        "target_roles": "all"
    })
    notice_ok = status == 201 and body.get("id")
    log("11.1", "Create notice", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", notice_ok,
        err=str(err) if err else (str(body) if not notice_ok else None))

    # Send notification to teacher
    if teacher_tokens:
        tname = list(teacher_tokens.keys())[0]
        tid = teacher_ids[tname]
        status, body, err = req("POST", "/api/notifications", admin_token, {
            "user_id": tid, "title": "Staff Meeting", "message": "Staff meeting on Friday at 3pm",
            "notification_type": "announcement", "category": "general"
        })
        notif_ok = status == 201 and body.get("id")
        log("11.2", "Send notification to teacher", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", notif_ok,
            err=str(err) if err else (str(body) if not notif_ok else None))

    # Send notification to student
    if student_tokens:
        sname = list(student_tokens.keys())[0]
        sid = student_ids[sname]
        status, body, err = req("POST", "/api/notifications", admin_token, {
            "user_id": sid, "title": "Exam Schedule", "message": "Mid-term exams start Aug 1",
            "notification_type": "exam", "category": "academic"
        })
        notif_ok = status == 201 and body.get("id")
        log("11.3", "Send notification to student", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", notif_ok,
            err=str(err) if err else (str(body) if not notif_ok else None))

    # Send notification to parent
    if parent_tokens:
        pname = list(parent_tokens.keys())[0]
        pid = parent_ids[pname]
        status, body, err = req("POST", "/api/notifications", admin_token, {
            "user_id": pid, "title": "Fee Reminder", "message": "Tuition fee due by Aug 31",
            "notification_type": "fee", "category": "finance"
        })
        notif_ok = status == 201 and body.get("id")
        log("11.4", "Send notification to parent", "201 + id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", notif_ok,
            err=str(err) if err else (str(body) if not notif_ok else None))

    # Verify delivery
    for tname, ttoken in teacher_tokens.items():
        if ttoken:
            status, body, err = req("GET", "/api/notifications", ttoken)
            log("11.5", f"Teacher {tname} receives notification", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))
    for sname, stoken in student_tokens.items():
        if stoken:
            status, body, err = req("GET", "/api/notifications", stoken)
            log("11.5", f"Student {sname} receives notification", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))
    for pname, ptoken in parent_tokens.items():
        if ptoken:
            status, body, err = req("GET", "/api/notifications", ptoken)
            log("11.5", f"Parent {pname} receives notification", "200 + data", f"{status}", status == 200,
                err=str(err) if err else (str(body) if status != 200 else None))

# =====================================================================
# SAVE RESULTS
# =====================================================================
with open("e2e_full_results.json", "w") as f:
    json.dump(results, f, indent=2)

passed = sum(1 for r in results if r["ok"])
failed = sum(1 for r in results if not r["ok"])
print("\n" + "=" * 80)
print(f"TOTAL: {len(results)} | PASSED: {passed} | FAILED: {failed}")
print("=" * 80)