"""End-to-end demo verification for School ERP - checks auth, roles, CRUD, workflows."""
import requests, json, sys
from datetime import date, timedelta

BASE = "http://127.0.0.1:8000"
results = []
PASSWORD = "admin123"

def log(module, test, status, detail=""):
    results.append({"module": module, "test": test, "status": status, "detail": str(detail)[:200]})
    emoji = "PASS" if status == "PASS" else "FAIL" if status == "FAIL" else "WARN"
    print(f"[{emoji}] {module} | {test}: {detail}")

def login(email, pw=PASSWORD):
    try:
        r = requests.post(f"{BASE}/auth/token", data={"username": email, "password": pw}, timeout=10)
        if r.status_code == 200:
            return r.json()["access_token"]
    except Exception as e:
        log("AUTH", f"Login {email}", "FAIL", str(e))
    return None

def H(tok): return {"Authorization": f"Bearer {tok}"}

def G(tok, path, params=None):
    try:
        r = requests.get(f"{BASE}{path}", headers=H(tok), params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e)})()

def P(tok, path, j=None, params=None):
    try:
        r = requests.post(f"{BASE}{path}", headers=H(tok), json=j, params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e)})()

def U(tok, path, j=None, params=None):
    try:
        r = requests.put(f"{BASE}{path}", headers=H(tok), json=j, params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e)})()

def D(tok, path, params=None):
    try:
        r = requests.delete(f"{BASE}{path}", headers=H(tok), params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e)})()

def check(module, test, resp, ok_codes, detail=""):
    ok = resp.status_code in ok_codes
    log(module, test, "PASS" if ok else "FAIL", f"{resp.status_code} {detail}")
    return ok

# ============ 1. SUPER ADMIN ============
sa_token = login("admin@school.local")
log("SuperAdmin", "Login", "PASS" if sa_token else "FAIL")

if sa_token:
    # Get list of schools
    r = G(sa_token, "/api/superadmin/schools", {"skip": 0, "limit": 50})
    schools = r.json() if r.status_code == 200 and isinstance(r.json(), list) else []
    check("SuperAdmin", "List Schools", r, [200], f"{len(schools)} schools")

    # Platform dashboard
    r = G(sa_token, "/api/superadmin/platform/dashboard")
    check("SuperAdmin", "Platform Dashboard", r, [200])

    # Audit logs
    r = G(sa_token, "/api/superadmin/audit-logs", {"skip": 0, "limit": 5})
    check("SuperAdmin", "Audit Logs", r, [200])

    # Subscriptions plans
    r = G(sa_token, "/api/superadmin/subscriptions/plans")
    check("SuperAdmin", "Subscription Plans", r, [200])

    # Pick a school for testing (or create one)
    sid = schools[0]["id"] if schools else None
    if not sid:
        r = P(sa_token, "/api/superadmin/schools", {"school_name": f"Demo School {date.today().isoformat()}", "school_code": f"DEMO{date.today().strftime('%m%d')}", "email": "demo@school.edu", "subscription_plan": "premium"})
        if r.status_code in (200, 201):
            sid = r.json().get("id")
    check("SuperAdmin", "School Read/Find", type("R", (), {"status_code": 200 if sid else 404})(), [200], f"sid={sid}")

    # School detail
    if sid:
        r = G(sa_token, f"/api/superadmin/schools/{sid}")
        check("SuperAdmin", "School Detail", r, [200])

        # School statistics
        r = G(sa_token, f"/api/superadmin/schools/{sid}/statistics")
        check("SuperAdmin", "School Stats", r, [200])

# ============ 2. SCHOOL ADMIN (school 1) ============
sa_t = login("schooladmin@default.school")
log("SchoolAdmin", "Login", "PASS" if sa_t else "FAIL")

if sa_t:
    r = G(sa_t, "/users/me")
    check("SchoolAdmin", "Profile", r, [200])
    r = G(sa_t, "/api/dashboard/summary")
    check("SchoolAdmin", "Dashboard Summary", r, [200])
    r = G(sa_t, "/api/settings")
    check("SchoolAdmin", "Settings Get", r, [200])

    # CRUD: Academic Years
    r = P(sa_t, "/api/academic-years", {"name": "2026-2027 Test", "start_date": "2026-06-01", "end_date": "2027-05-31", "is_active": True})
    ay_ok = r.status_code in (200, 201)
    ay_id = r.json().get("id") if ay_ok else None
    check("SchoolAdmin", "AY Create", r, [200, 201], f"id={ay_id}")
    if ay_id:
        r = G(sa_t, f"/api/academic-years/{ay_id}")
        check("SchoolAdmin", "AY Read", r, [200])
        r = U(sa_t, f"/api/academic-years/{ay_id}", {"name": "2026-2027 Updated"})
        check("SchoolAdmin", "AY Update", r, [200])
        r = D(sa_t, f"/api/academic-years/{ay_id}")
        check("SchoolAdmin", "AY Delete", r, [200, 204])

    # CRUD: Classes
    r = P(sa_t, "/api/classes", {"name": "Demo Class", "class_code": "DC01"})
    cls_ok = r.status_code in (200, 201)
    cls_id = r.json().get("id") if cls_ok else None
    check("SchoolAdmin", "Class Create", r, [200, 201], f"id={cls_id}")
    if cls_id:
        r = U(sa_t, f"/api/classes/{cls_id}", {"name": "Demo Class Renamed"})
        check("SchoolAdmin", "Class Update", r, [200])
        r = D(sa_t, f"/api/classes/{cls_id}")
        check("SchoolAdmin", "Class Delete", r, [200, 204])

    # Read-only checks on core modules
    for mod, path in [("Students", "/api/students"), ("Teachers", "/api/teachers"), ("Parents", "/api/parents"),
                      ("Subjects", "/api/subjects"), ("Sections", "/api/sections"), ("Exams", "/api/exams"),
                      ("ExamResults", "/api/exam-results"), ("Enrollments", "/api/enrollments"),
                      ("Fees", "/api/fee-structures"), ("Payments", "/api/payments"), ("Notices", "/api/notices"),
                      ("Events", "/api/events"), ("Certificates", "/api/certificates"),
                      ("Attendances", "/api/attendances"), ("Homework", "/api/homeworks"),
                      ("Rooms", "/api/rooms"), ("Timetable", "/api/timetable")]:
        r = G(sa_t, path, {"skip": 0, "limit": 20})
        check("SchoolAdmin", f"{mod} List", r, [200])

# ============ 3. TEACHER (school 2) ============
t_tok = login("teacher1@testalpha.edu", "TeacherPass123!")
log("Teacher", "Login", "PASS" if t_tok else "FAIL")

if t_tok:
    r = G(t_tok, "/users/me")
    check("Teacher", "Profile", r, [200])
    # Teacher portal endpoints
    for mod, path in [("Dashboard", "/api/portal/teacher/dashboard"), ("Classes", "/api/portal/teacher/classes"),
                      ("Students", "/api/portal/teacher/students"), ("Exams", "/api/portal/teacher/exams"),
                      ("Homework", "/api/portal/teacher/homework"), ("Notices", "/api/portal/teacher/notices"),
                      ("Calendar", "/api/portal/teacher/calendar"), ("Messages", "/api/portal/teacher/messages")]:
        r = G(t_tok, path)
        check("Teacher", f"{mod} Portal", r, [200])

# ============ 4. STUDENT (school 2) ============
st_tok = login("student_stu001@testalpha.edu", "StudentPass123!")
log("Student", "Login", "PASS" if st_tok else "FAIL")

if st_tok:
    r = G(st_tok, "/users/me")
    check("Student", "Profile", r, [200])
    for mod, path in [("Dashboard", "/api/portal/student/dashboard"), ("Attendance", "/api/portal/student/attendance"),
                      ("Homework", "/api/portal/student/homework"), ("Exams", "/api/portal/student/exams"),
                      ("Fees", "/api/portal/student/fees"), ("Notices", "/api/portal/student/notices"),
                      ("Calendar", "/api/portal/student/calendar"), ("Documents", "/api/portal/student/documents"),
                      ("Messages", "/api/portal/student/messages")]:
        r = G(st_tok, path)
        check("Student", f"{mod} Portal", r, [200])

# ============ 5. PARENT (school 2) ============
p_tok = login("john.anderson@email.com", "ParentPass123!")
log("Parent", "Login", "PASS" if p_tok else "FAIL")

if p_tok:
    r = G(p_tok, "/users/me")
    check("Parent", "Profile", r, [200])
    r = G(p_tok, "/api/portal/parent/dashboard")
    check("Parent", "Dashboard", r, [200])
    r = G(p_tok, "/api/portal/parent/children")
    check("Parent", "Children", r, [200])
    # Get first child for subsequent requests
    children_data = r.json() if r.status_code == 200 else {}
    children = children_data.get("children", [])
    student_id = children[0]["student_id"] if children and len(children) > 0 else None
    if student_id:
        for mod, path in [("Attendance", f"/api/portal/parent/children/{student_id}/attendance"), 
                          ("Homework", f"/api/portal/parent/children/{student_id}/homework"),
                          ("Exams", f"/api/portal/parent/children/{student_id}/results"), 
                          ("Fees", f"/api/portal/parent/children/{student_id}/fees"),
                          ("Notices", "/api/portal/parent/notices"), 
                          ("Calendar", "/api/portal/parent/calendar"),
                          ("Messages", "/api/portal/parent/messages")]:
            r = G(p_tok, path)
            check("Parent", f"{mod} Portal", r, [200])
    else:
        log("Parent", "Attendance Portal", "SKIP", "No children found")
        log("Parent", "Homework Portal", "SKIP", "No children found")
        log("Parent", "Exams Portal", "SKIP", "No children found")
        log("Parent", "Fees Portal", "SKIP", "No children found")

# ============ 6. NOTIFICATIONS ============
if sa_token:
    r = G(sa_token, "/api/notifications/unread")
    check("Notifications", "Unread", r, [200])

# ============ 7. ROLE-BASED ACCESS CONTROL ============
if sa_t:
    # School admin should NOT access super admin routes
    r = G(sa_t, "/api/superadmin/schools")
    log("RBAC", "SchoolAdmin->SuperAdmin blocked", "PASS" if r.status_code in (403, 404) else "FAIL", f"{r.status_code}")
    # Student should NOT access admin routes
    if st_tok:
        r = G(st_tok, "/api/students")
        log("RBAC", "Student->Admin blocked", "PASS" if r.status_code in (403, 404) else "FAIL", f"{r.status_code}")
    # Teacher should NOT access admin-only (parent create)
    if t_tok:
        r = P(t_tok, "/api/parents", {"phone": "555", "address": "x", "school_id": 2})
        log("RBAC", "Teacher->ParentCreate blocked", "PASS" if r.status_code in (403, 404) else "FAIL", f"{r.status_code}")

# ============ 8. REPORT CARDS (may be partial) ============
if sa_t:
    r = G(sa_t, "/api/report-cards", {"skip": 0, "limit": 10})
    check("ReportCards", "List", r, [200])

# ============ SUMMARY ============
total = len(results)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
print(f"\n{'='*60}")
print(f"TOTAL: {total} | PASS: {passed} | FAIL: {failed}")
print(f"{'='*60}\n")

with open("demo_verification_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Results saved to demo_verification_results.json")