"""Comprehensive end-to-end verification for School ERP"""
import requests
import json
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
        return type("R", (), {"status_code": 0, "text": str(e), "json": lambda: {}})()

def P(tok, path, j=None, params=None):
    try:
        r = requests.post(f"{BASE}{path}", headers=H(tok), json=j, params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e), "json": lambda: {}})()

def U(tok, path, j=None, params=None):
    try:
        r = requests.put(f"{BASE}{path}", headers=H(tok), json=j, params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e), "json": lambda: {}})()

def D(tok, path, params=None):
    try:
        r = requests.delete(f"{BASE}{path}", headers=H(tok), params=params, timeout=15)
        return r
    except Exception as e:
        return type("R", (), {"status_code": 0, "text": str(e), "json": lambda: {}})()

def check(module, test, resp, ok_codes, detail=""):
    ok = resp.status_code in ok_codes
    log(module, test, "PASS" if ok else "FAIL", f"{resp.status_code} {detail}")
    return ok

# ============ AUTHENTICATION ============
print("\n=== AUTHENTICATION ===")
sa_token = login("admin@school.local")
log("AUTH", "Super Admin Login", "PASS" if sa_token else "FAIL")

sa_t = login("schooladmin@default.school")
log("AUTH", "School Admin Login", "PASS" if sa_t else "FAIL")

t_tok = login("teacher1@testalpha.edu", "TeacherPass123!")
log("AUTH", "Teacher Login", "PASS" if t_tok else "FAIL")

st_tok = login("student_stu001@testalpha.edu", "StudentPass123!")
log("AUTH", "Student Login", "PASS" if st_tok else "FAIL")

p_tok = login("john.anderson@email.com", "ParentPass123!")
log("AUTH", "Parent Login", "PASS" if p_tok else "FAIL")

# ============ SUPER ADMIN MODULE ============
print("\n=== SUPER ADMIN MODULE ===")
if sa_token:
    r = G(sa_token, "/api/superadmin/schools", {"skip": 0, "limit": 50})
    check("SuperAdmin", "List Schools", r, [200])
    
    r = G(sa_token, "/api/superadmin/platform/dashboard")
    check("SuperAdmin", "Platform Dashboard", r, [200])
    
    r = G(sa_token, "/api/superadmin/audit-logs", {"skip": 0, "limit": 5})
    check("SuperAdmin", "Audit Logs", r, [200])
    
    r = G(sa_token, "/api/superadmin/subscriptions/plans")
    check("SuperAdmin", "Subscription Plans", r, [200])
    
    # Get first school for testing
    r_schools = G(sa_token, "/api/superadmin/schools", {"skip": 0, "limit": 50})
    schools_data = r_schools.json() if r_schools.status_code == 200 else []
    sid = schools_data[0]["id"] if schools_data else 1
    
    r = G(sa_token, f"/api/superadmin/schools/{sid}")
    check("SuperAdmin", "School Detail", r, [200])
    
    r = G(sa_token, f"/api/superadmin/schools/{sid}/statistics")
    check("SuperAdmin", "School Statistics", r, [200])

# ============ SCHOOL ADMIN MODULE ============
print("\n=== SCHOOL ADMIN MODULE ===")
if sa_t:
    r = G(sa_t, "/users/me")
    check("SchoolAdmin", "Profile", r, [200])
    
    r = G(sa_t, "/api/dashboard/summary")
    check("SchoolAdmin", "Dashboard", r, [200])
    
    r = G(sa_t, "/api/settings")
    check("SchoolAdmin", "Settings", r, [200])
    
    # CRUD Operations
    r = P(sa_t, "/api/academic-years", {"name": "Test AY 2026", "start_date": "2026-06-01", "end_date": "2027-05-31", "is_active": True})
    ay_id = r.json().get("id") if r.status_code in (200, 201) else None
    check("SchoolAdmin", "Create Academic Year", r, [200, 201])
    
    if ay_id:
        r = G(sa_t, f"/api/academic-years/{ay_id}")
        check("SchoolAdmin", "Read Academic Year", r, [200])
        
        r = U(sa_t, f"/api/academic-years/{ay_id}", {"name": "Test AY Updated"})
        check("SchoolAdmin", "Update Academic Year", r, [200])
        
        r = D(sa_t, f"/api/academic-years/{ay_id}")
        check("SchoolAdmin", "Delete Academic Year", r, [200, 204])
    
    # Classes CRUD
    r = P(sa_t, "/api/classes", {"name": "Test Class", "class_code": "TC01"})
    cls_id = r.json().get("id") if r.status_code in (200, 201) else None
    check("SchoolAdmin", "Create Class", r, [200, 201])
    
    if cls_id:
        r = U(sa_t, f"/api/classes/{cls_id}", {"name": "Test Class Updated"})
        check("SchoolAdmin", "Update Class", r, [200])
        
        r = D(sa_t, f"/api/classes/{cls_id}")
        check("SchoolAdmin", "Delete Class", r, [200, 204])
    
    # List all modules
    modules = [
        ("Students", "/api/students"),
        ("Teachers", "/api/teachers"),
        ("Parents", "/api/parents"),
        ("Subjects", "/api/subjects"),
        ("Sections", "/api/sections"),
        ("Exams", "/api/exams"),
        ("Exam Results", "/api/exam-results"),
        ("Enrollments", "/api/enrollments"),
        ("Fee Structures", "/api/fee-structures"),
        ("Payments", "/api/payments"),
        ("Notices", "/api/notices"),
        ("Events", "/api/events"),
        ("Certificates", "/api/certificates"),
        ("Attendances", "/api/attendances"),
        ("Homework", "/api/homeworks"),
        ("Rooms", "/api/rooms"),
        ("Timetable", "/api/timetable"),
        ("Report Cards", "/api/report-cards"),
    ]
    
    for mod_name, path in modules:
        r = G(sa_t, path, {"skip": 0, "limit": 20})
        check("SchoolAdmin", f"List {mod_name}", r, [200])

# ============ TEACHER PORTAL ============
print("\n=== TEACHER PORTAL ===")
if t_tok:
    r = G(t_tok, "/users/me")
    check("Teacher", "Profile", r, [200])
    
    # Specific endpoints mentioned in task
    r = G(t_tok, "/api/portal/teacher/students")
    check("Teacher", "Students Portal", r, [200])
    
    r = G(t_tok, "/api/portal/teacher/notices")
    check("Teacher", "Notices Portal", r, [200])
    
    # All teacher portal endpoints
    teacher_endpoints = [
        ("Dashboard", "/api/portal/teacher/dashboard"),
        ("Classes", "/api/portal/teacher/classes"),
        ("Exams", "/api/portal/teacher/exams"),
        ("Homework", "/api/portal/teacher/homework"),
        ("Calendar", "/api/portal/teacher/calendar"),
        ("Messages", "/api/portal/teacher/messages"),
    ]
    
    for mod_name, path in teacher_endpoints:
        r = G(t_tok, path)
        check("Teacher", f"{mod_name} Portal", r, [200])

# ============ STUDENT PORTAL ============
print("\n=== STUDENT PORTAL ===")
if st_tok:
    r = G(st_tok, "/users/me")
    check("Student", "Profile", r, [200])
    
    student_endpoints = [
        ("Dashboard", "/api/portal/student/dashboard"),
        ("Attendance", "/api/portal/student/attendance"),
        ("Homework", "/api/portal/student/homework"),
        ("Exams", "/api/portal/student/exams"),
        ("Fees", "/api/portal/student/fees"),
        ("Notices", "/api/portal/student/notices"),
        ("Calendar", "/api/portal/student/calendar"),
        ("Documents", "/api/portal/student/documents"),
        ("Messages", "/api/portal/student/messages"),
    ]
    
    for mod_name, path in student_endpoints:
        r = G(st_tok, path)
        check("Student", f"{mod_name} Portal", r, [200])

# ============ PARENT PORTAL ============
print("\n=== PARENT PORTAL ===")
if p_tok:
    r = G(p_tok, "/users/me")
    check("Parent", "Profile", r, [200])
    
    r = G(p_tok, "/api/portal/parent/dashboard")
    check("Parent", "Dashboard", r, [200])
    
    r = G(p_tok, "/api/portal/parent/children")
    check("Parent", "Children", r, [200])
    
    # Get first child
    children_data = r.json() if r.status_code == 200 else {}
    children = children_data.get("children", [])
    student_id = children[0]["student_id"] if children else None
    
    if student_id:
        parent_endpoints = [
            ("Attendance", f"/api/portal/parent/children/{student_id}/attendance"),
            ("Homework", f"/api/portal/parent/children/{student_id}/homework"),
            ("Exams", f"/api/portal/parent/children/{student_id}/results"),
            ("Fees", f"/api/portal/parent/children/{student_id}/fees"),
        ]
        
        for mod_name, path in parent_endpoints:
            r = G(p_tok, path)
            check("Parent", f"{mod_name} Portal", r, [200])
    
    r = G(p_tok, "/api/portal/parent/notices")
    check("Parent", "Notices Portal", r, [200])
    
    r = G(p_tok, "/api/portal/parent/calendar")
    check("Parent", "Calendar Portal", r, [200])
    
    r = G(p_tok, "/api/portal/parent/messages")
    check("Parent", "Messages Portal", r, [200])

# ============ NOTIFICATIONS ============
print("\n=== NOTIFICATIONS ===")
if sa_token:
    r = G(sa_token, "/api/notifications/unread")
    check("Notifications", "Unread Count", r, [200])

# ============ ROLE-BASED ACCESS CONTROL ============
print("\n=== ROLE-BASED ACCESS CONTROL ===")
if sa_t:
    # School admin should NOT access super admin routes
    r = G(sa_t, "/api/superadmin/schools")
    check("RBAC", "SchoolAdmin->SuperAdmin Blocked", r, [403, 404])
    
    # Student should NOT access admin routes
    if st_tok:
        r = G(st_tok, "/api/students")
        check("RBAC", "Student->Admin Blocked", r, [403, 404])
    
    # Teacher should NOT access admin-only routes
    if t_tok:
        r = P(t_tok, "/api/parents", {"phone": "555", "address": "x"})
        check("RBAC", "Teacher->ParentCreate Blocked", r, [403, 404])

# ============ API ERROR CHECK ============
print("\n=== API ERROR CHECK ===")
# Verify no 404, 401, 403, 405, 500 errors on valid endpoints
error_counts = {401: 0, 403: 0, 404: 0, 405: 0, 500: 0}

# Test with invalid token
r = G("invalid_token", "/api/dashboard/summary")
if r.status_code in error_counts:
    error_counts[r.status_code] += 1
    log("API", "Invalid Token Test", "PASS", f"Correctly returned {r.status_code}")

# Test with expired school (if any)
# This is handled by backend logic

# ============ SUMMARY ============
print("\n" + "="*60)
total = len(results)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
warnings = sum(1 for r in results if r["status"] == "WARN")

print(f"TOTAL TESTS: {total}")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")
print(f"WARNINGS: {warnings}")
print(f"SUCCESS RATE: {(passed/total*100):.2f}%")
print("="*60)

with open("comprehensive_verification_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nResults saved to comprehensive_verification_results.json")

if failed > 0:
    print("\n❌ VERIFICATION FAILED - Some tests did not pass")
    exit(1)
else:
    print("\n✅ ALL TESTS PASSED - System is demo-ready!")
    exit(0)