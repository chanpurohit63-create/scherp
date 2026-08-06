"""Comprehensive QA Test - All 19 Modules with 14 test points each"""
import requests, json, sys, time
from datetime import date, datetime, timedelta

BASE = "http://localhost:8000"
results = []
module_results = {}

def log(module, test, status, detail=""):
    results.append({"module": module, "test": test, "status": status, "detail": detail})
    emoji = "PASS" if status == "PASS" else "FAIL" if status == "FAIL" else "WARN"
    print(f"  [{emoji}] {test}: {detail}")

def login(email, pw):
    r = requests.post(f"{BASE}/auth/token", data={"username": email, "password": pw})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

def H(tok): return {"Authorization": f"Bearer {tok}"}
def G(tok, path, params=None): return requests.get(f"{BASE}{path}", headers=H(tok), params=params)
def P(tok, path, j=None, params=None): return requests.post(f"{BASE}{path}", headers=H(tok), json=j, params=params)
def U(tok, path, j=None, params=None): return requests.put(f"{BASE}{path}", headers=H(tok), json=j, params=params)
def D(tok, path): return requests.delete(f"{BASE}{path}", headers=H(tok))

def start_module(name):
    module_results[name] = {"PASS": 0, "FAIL": 0, "WARN": 0}
    print(f"\n{'='*60}")
    print(f"MODULE: {name}")
    print(f"{'='*60}")

def end_module(name):
    d = module_results[name]
    total = d["PASS"] + d["FAIL"] + d["WARN"]
    print(f"  --- {name}: {total} tests | PASS={d['PASS']} FAIL={d['FAIL']} WARN={d['WARN']}")

def check(module, test, status, detail=""):
    module_results[module][status] = module_results[module].get(status, 0) + 1
    log(module, test, status, detail)

# ========== LOGIN ==========
print("="*60)
print("SETUP: Login and get tokens")
print("="*60)

sa = login("admin@school.local", "admin123")
print(f"  Super Admin login: {'PASS' if sa else 'FAIL'}")

# Greenwood school admin
sat = login("admin@greenwood.edu", "NewGreenwood@2026")
if not sat:
    sat = login("admin@greenwood.edu", "Greenwood@2026")
print(f"  School Admin login: {'PASS' if sat else 'FAIL'}")

# Teacher
tt = login("priya.sharma@greenwood.edu", "Teacher1@2026")
print(f"  Teacher login: {'PASS' if tt else 'FAIL'}")

# Student
st = login("student_stu2026001@greenwood.edu", "Student1@2026")
print(f"  Student login: {'PASS' if st else 'FAIL'}")

# Parent
pt = login("rajesh.sharma@email.com", "Parent1@2026")
print(f"  Parent login: {'PASS' if pt else 'FAIL'}")

if not sat:
    print("FATAL: Cannot login as school admin. Aborting.")
    sys.exit(1)

tok = sat  # Use school admin token for most tests

# ========== 1. SCHOOLS MODULE ==========
start_module("Schools")
# Read
r = G(sa, "/api/superadmin/schools")
check("Schools", "List Schools", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
schools = r.json() if r.status_code == 200 else []
sid = next((s["id"] for s in schools if s.get("school_code") == "GIS2026"), None)
check("Schools", "Find Greenwood", "PASS" if sid else "FAIL", f"ID={sid}")

# Read single
if sid:
    r = G(sa, f"/api/superadmin/schools/{sid}")
    check("Schools", "Get School", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(sa, "/api/superadmin/schools", j={"school_name": "QA Test School", "school_code": "QATS001", "email": "qa@test.edu", "phone": "555-9999", "address": "123 QA Lane"})
new_sid = r.json().get("id") if r.status_code in (200, 201) else None
check("Schools", "Create School", "PASS" if new_sid else "FAIL", f"ID={new_sid}")

# Update
if new_sid:
    r = U(sa, f"/api/superadmin/schools/{new_sid}", j={"school_name": "QA Test School Updated"})
    check("Schools", "Update School", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Search
r = G(sa, "/api/superadmin/schools", params={"search": "Greenwood"})
check("Schools", "Search", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Filter
r = G(sa, "/api/superadmin/schools", params={"status_filter": "active"})
check("Schools", "Filter", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Pagination
r = G(sa, "/api/superadmin/schools", params={"skip": 0, "limit": 2})
check("Schools", "Pagination", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Form validation (missing required field)
r = P(sa, "/api/superadmin/schools", j={"school_name": ""})
check("Schools", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

# Delete (cleanup)
if new_sid:
    r = D(sa, f"/api/superadmin/schools/{new_sid}")
    check("Schools", "Delete School", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Schools")

# ========== 2. STUDENTS MODULE ==========
start_module("Students")
# Read
r = G(tok, "/api/students")
check("Students", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
students = r.json() if r.status_code == 200 else []
check("Students", "Data Present", "PASS" if len(students) > 0 else "FAIL", f"{len(students)} students")

# Read single
if students:
    stid = students[0]["id"]
    r = G(tok, f"/api/students/{stid}")
    check("Students", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/students", j={"user_id": 19, "admission_no": "QA-STU-001", "dob": "2015-01-01", "gender": "M", "admission_date": str(date.today())})
new_stid = r.json().get("id") if r.status_code in (200, 201) else None
check("Students", "Create", "PASS" if new_stid else "FAIL", f"ID={new_stid}")

# Update
if new_stid:
    r = U(tok, f"/api/students/{new_stid}", j={"admission_no": "QA-STU-001-UPD"})
    check("Students", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Search
r = G(tok, "/api/students", params={"query": "Aarav"})
check("Students", "Search", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Filter
r = G(tok, "/api/students", params={"status": "active"})
check("Students", "Filter", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Pagination
r = G(tok, "/api/students", params={"skip": 0, "limit": 2})
check("Students", "Pagination", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Form validation
r = P(tok, "/api/students", j={})
check("Students", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

# Delete
if new_stid:
    r = D(tok, f"/api/students/{new_stid}")
    check("Students", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Students")

# ========== 3. TEACHERS MODULE ==========
start_module("Teachers")
r = G(tok, "/api/teachers")
check("Teachers", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
teachers = r.json() if r.status_code == 200 else []
check("Teachers", "Data Present", "PASS" if len(teachers) > 0 else "FAIL", f"{len(teachers)} teachers")

if teachers:
    tid = teachers[0]["id"]
    r = G(tok, f"/api/teachers/{tid}")
    check("Teachers", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/teachers", j={"user_id": 18, "employee_no": "QA-EMP-001", "hire_date": str(date.today())})
new_tid = r.json().get("id") if r.status_code in (200, 201) else None
check("Teachers", "Create", "PASS" if new_tid else "FAIL", f"ID={new_tid}")

if new_tid:
    r = U(tok, f"/api/teachers/{new_tid}", j={"employee_no": "QA-EMP-001-UPD"})
    check("Teachers", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = G(tok, "/api/teachers", params={"query": "Priya"})
check("Teachers", "Search", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = G(tok, "/api/teachers", params={"status": "true"})
check("Teachers", "Filter", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = G(tok, "/api/teachers", params={"skip": 0, "limit": 2})
check("Teachers", "Pagination", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/teachers", j={})
check("Teachers", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_tid:
    r = D(tok, f"/api/teachers/{new_tid}")
    check("Teachers", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Teachers")

# ========== 4. PARENTS MODULE ==========
start_module("Parents")
r = G(tok, "/api/parents")
check("Parents", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
parents = r.json() if r.status_code == 200 else []
check("Parents", "Data Present", "PASS" if len(parents) > 0 else "FAIL", f"{len(parents)} parents")

if parents:
    pid = parents[0]["id"]
    r = G(tok, f"/api/parents/{pid}")
    check("Parents", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/parents", j={"user_id": 24, "phone": "555-1234", "address": "QA Address"})
new_pid = r.json().get("id") if r.status_code in (200, 201) else None
check("Parents", "Create", "PASS" if new_pid else "FAIL", f"ID={new_pid}")

if new_pid:
    r = U(tok, f"/api/parents/{new_pid}", j={"phone": "555-5678"})
    check("Parents", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/parents", j={})
check("Parents", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_pid:
    r = D(tok, f"/api/parents/{new_pid}")
    check("Parents", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Parents")

# ========== 5. CLASSES MODULE ==========
start_module("Classes")
r = G(tok, "/api/classes")
check("Classes", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
classes = r.json() if r.status_code == 200 else []
check("Classes", "Data Present", "PASS" if len(classes) > 0 else "FAIL", f"{len(classes)} classes")

if classes:
    cid = classes[0]["id"]
    r = G(tok, f"/api/classes/{cid}")
    check("Classes", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/classes", j={"name": "QA Class 1", "grade_level": "QA"})
new_cid = r.json().get("id") if r.status_code in (200, 201) else None
check("Classes", "Create", "PASS" if new_cid else "FAIL", f"ID={new_cid}")

if new_cid:
    r = U(tok, f"/api/classes/{new_cid}", j={"name": "QA Class 1 Updated"})
    check("Classes", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/classes", j={})
check("Classes", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_cid:
    r = D(tok, f"/api/classes/{new_cid}")
    check("Classes", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Classes")

# ========== 6. SECTIONS MODULE ==========
start_module("Sections")
r = G(tok, "/api/sections")
check("Sections", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
sections = r.json() if r.status_code == 200 else []
check("Sections", "Data Present", "PASS" if len(sections) > 0 else "FAIL", f"{len(sections)} sections")

if sections:
    secid = sections[0]["id"]
    r = G(tok, f"/api/sections/{secid}")
    check("Sections", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
if classes:
    cid = classes[0]["id"]
    r = P(tok, "/api/sections", j={"name": "QA Sec", "class_id": cid})
    new_secid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Sections", "Create", "PASS" if new_secid else "FAIL", f"ID={new_secid}")

    if new_secid:
        r = U(tok, f"/api/sections/{new_secid}", j={"name": "QA Sec Updated"})
        check("Sections", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

    r = P(tok, "/api/sections", j={})
    check("Sections", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

    if new_secid:
        r = D(tok, f"/api/sections/{new_secid}")
        check("Sections", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Sections")

# ========== 7. SUBJECTS MODULE ==========
start_module("Subjects")
r = G(tok, "/api/subjects")
check("Subjects", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
subjects = r.json() if r.status_code == 200 else []
check("Subjects", "Data Present", "PASS" if len(subjects) > 0 else "FAIL", f"{len(subjects)} subjects")

if subjects:
    subid = subjects[0]["id"]
    r = G(tok, f"/api/subjects/{subid}")
    check("Subjects", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/subjects", j={"name": "QA Subject", "code": "QAS"})
new_subid = r.json().get("id") if r.status_code in (200, 201) else None
check("Subjects", "Create", "PASS" if new_subid else "FAIL", f"ID={new_subid}")

if new_subid:
    r = U(tok, f"/api/subjects/{new_subid}", j={"name": "QA Subject Updated"})
    check("Subjects", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/subjects", j={})
check("Subjects", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_subid:
    r = D(tok, f"/api/subjects/{new_subid}")
    check("Subjects", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Subjects")

# ========== 8. ACADEMIC YEARS MODULE ==========
start_module("Academic Years")
r = G(tok, "/api/academic-years")
check("Academic Years", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
years = r.json() if r.status_code == 200 else []
check("Academic Years", "Data Present", "PASS" if len(years) > 0 else "FAIL", f"{len(years)} years")

if years:
    ayid = years[0]["id"]
    r = G(tok, f"/api/academic-years/{ayid}")
    check("Academic Years", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/academic-years", j={"name": "QA-2027", "start_date": "2027-06-01", "end_date": "2028-05-31", "is_active": False})
new_ayid = r.json().get("id") if r.status_code in (200, 201) else None
check("Academic Years", "Create", "PASS" if new_ayid else "FAIL", f"ID={new_ayid}")

if new_ayid:
    r = U(tok, f"/api/academic-years/{new_ayid}", j={"name": "QA-2027-Updated"})
    check("Academic Years", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/academic-years", j={})
check("Academic Years", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_ayid:
    r = D(tok, f"/api/academic-years/{new_ayid}")
    check("Academic Years", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Academic Years")

# ========== 9. ATTENDANCE MODULE ==========
start_module("Attendance")
r = G(tok, "/api/attendances")
check("Attendance", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
attendances = r.json() if r.status_code == 200 else []
check("Attendance", "Data Present", "PASS" if len(attendances) > 0 else "FAIL", f"{len(attendances)} records")

if attendances:
    attid = attendances[0]["id"]
    r = G(tok, f"/api/attendances/{attid}")
    check("Attendance", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
if students:
    stid = students[0]["id"]
    r = P(tok, "/api/attendances", j={"student_id": stid, "date": str(date.today()), "status": "present"})
    new_attid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Attendance", "Create", "PASS" if new_attid else "FAIL", f"ID={new_attid}")

    if new_attid:
        r = U(tok, f"/api/attendances/{new_attid}", j={"status": "absent"})
        check("Attendance", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

    r = P(tok, "/api/attendances", j={})
    check("Attendance", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

    if new_attid:
        r = D(tok, f"/api/attendances/{new_attid}")
        check("Attendance", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Attendance")

# ========== 10. HOMEWORK MODULE ==========
start_module("Homework")
r = G(tok, "/api/homeworks")
check("Homework", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
homeworks = r.json() if r.status_code == 200 else []
check("Homework", "Data Present", "PASS" if len(homeworks) > 0 else "FAIL", f"{len(homeworks)} records")

if homeworks:
    hwid = homeworks[0]["id"]
    r = G(tok, f"/api/homeworks/{hwid}")
    check("Homework", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
if classes and students:
    cid = classes[0]["id"]
    r = P(tok, "/api/homeworks", j={"title": "QA HW", "description": "QA Test HW", "assigned_by": 17, "class_id": cid, "due_date": str(date.today() + timedelta(days=7))})
    new_hwid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Homework", "Create", "PASS" if new_hwid else "FAIL", f"ID={new_hwid}")

    if new_hwid:
        r = U(tok, f"/api/homeworks/{new_hwid}", j={"title": "QA HW Updated"})
        check("Homework", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

    r = P(tok, "/api/homeworks", j={})
    check("Homework", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

    if new_hwid:
        r = D(tok, f"/api/homeworks/{new_hwid}")
        check("Homework", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Homework")

# ========== 11. EXAMS MODULE ==========
start_module("Exams")
r = G(tok, "/api/exams")
check("Exams", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
exams = r.json() if r.status_code == 200 else []
check("Exams", "Data Present", "PASS" if len(exams) > 0 else "FAIL", f"{len(exams)} exams")

if exams:
    exid = exams[0]["id"]
    r = G(tok, f"/api/exams/{exid}")
    check("Exams", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
if years:
    ayid = years[0]["id"]
    r = P(tok, "/api/exams", j={"name": "QA Exam", "academic_year_id": ayid})
    new_exid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Exams", "Create", "PASS" if new_exid else "FAIL", f"ID={new_exid}")

    if new_exid:
        r = U(tok, f"/api/exams/{new_exid}", j={"name": "QA Exam Updated"})
        check("Exams", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

    r = P(tok, "/api/exams", j={})
    check("Exams", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

    if new_exid:
        r = D(tok, f"/api/exams/{new_exid}")
        check("Exams", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Exams")

# ========== 12. FEES MODULE ==========
start_module("Fees")
r = G(tok, "/api/fee-structures")
check("Fees", "List Structures", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
fee_structs = r.json() if r.status_code == 200 else []
check("Fees", "Data Present", "PASS" if len(fee_structs) > 0 else "FAIL", f"{len(fee_structs)} structures")

# Create fee structure
r = P(tok, "/api/fee-structures", j={"name": "QA Fee", "amount": 1000, "category": "tuition"})
new_fsid = r.json().get("id") if r.status_code in (200, 201) else None
check("Fees", "Create Structure", "PASS" if new_fsid else "FAIL", f"ID={new_fsid}")

if new_fsid:
    r = U(tok, f"/api/fee-structures/{new_fsid}", j={"amount": 1500})
    check("Fees", "Update Structure", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Fee assignments
r = G(tok, "/api/fee-assignments")
check("Fees", "List Assignments", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

if students and new_fsid:
    stid = students[0]["id"]
    r = P(tok, "/api/fee-assignments", j={"student_id": stid, "fee_structure_id": new_fsid, "due_date": str(date.today() + timedelta(days=30))})
    new_faid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Fees", "Create Assignment", "PASS" if new_faid else "FAIL", f"ID={new_faid}")

    if new_faid:
        r = U(tok, f"/api/fee-assignments/{new_faid}", j={"is_paid": True})
        check("Fees", "Update Assignment", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

        # Delete assignment
        r = D(tok, f"/api/fee-assignments/{new_faid}")
        check("Fees", "Delete Assignment", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")

r = P(tok, "/api/fee-structures", j={})
check("Fees", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_fsid:
    r = D(tok, f"/api/fee-structures/{new_fsid}")
    check("Fees", "Delete Structure", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Fees")

# ========== 13. PAYMENTS MODULE ==========
start_module("Payments")
r = G(tok, "/api/payments")
check("Payments", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
payments = r.json() if r.status_code == 200 else []
check("Payments", "Data Present", "PASS" if len(payments) > 0 else "FAIL", f"{len(payments)} payments")

if payments:
    payid = payments[0]["id"]
    r = G(tok, f"/api/payments/{payid}")
    check("Payments", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
if payments:
    faid = payments[0]["fee_assignment_id"]
    r = P(tok, "/api/payments", j={"fee_assignment_id": faid, "amount": 500, "reference": "QA-PAY-001"})
    new_payid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Payments", "Create", "PASS" if new_payid else "FAIL", f"ID={new_payid}")

    if new_payid:
        r = U(tok, f"/api/payments/{new_payid}", j={"amount": 600})
        check("Payments", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

    r = P(tok, "/api/payments", j={})
    check("Payments", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

    if new_payid:
        r = D(tok, f"/api/payments/{new_payid}")
        check("Payments", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Payments")

# ========== 14. TIMETABLE MODULE ==========
start_module("Timetable")
r = G(tok, "/api/timetable")
check("Timetable", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
timetables = r.json() if r.status_code == 200 else []
check("Timetable", "Data Present", "PASS" if len(timetables) > 0 else "FAIL", f"{len(timetables)} entries")

# Create
if classes and subjects and teachers and years:
    cid = classes[0]["id"]
    subid = subjects[0]["id"]
    tid = teachers[0]["id"]
    ayid = years[0]["id"]
    r = P(tok, "/api/timetable", j={"class_id": cid, "subject_id": subid, "teacher_id": tid, "day_of_week": 0, "period": 1, "start_time": "09:00", "end_time": "09:45", "academic_year_id": ayid})
    new_ttid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Timetable", "Create", "PASS" if new_ttid else "FAIL", f"ID={new_ttid}")

    if new_ttid:
        r = U(tok, f"/api/timetable/{new_ttid}", j={"period": 2})
        check("Timetable", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

    r = P(tok, "/api/timetable", j={})
    check("Timetable", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

    if new_ttid:
        r = D(tok, f"/api/timetable/{new_ttid}")
        check("Timetable", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Timetable")

# ========== 15. REPORT CARDS MODULE ==========
start_module("Report Cards")
r = G(tok, "/api/report-cards")
check("Report Cards", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
report_cards = r.json() if r.status_code == 200 else []
check("Report Cards", "Data Present", "PASS" if len(report_cards) > 0 else "FAIL", f"{len(report_cards)} cards")

if report_cards:
    rcid = report_cards[0]["id"]
    r = G(tok, f"/api/report-cards/{rcid}")
    check("Report Cards", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Generate
if students and exams and years:
    stid = students[0]["id"]
    exid = exams[0]["id"]
    ayid = years[0]["id"]
    r = P(tok, "/api/report-cards/generate", j={"student_id": stid, "exam_id": exid, "academic_year_id": ayid})
    check("Report Cards", "Generate", "PASS" if r.status_code in (200, 201) else "FAIL", f"{r.status_code}")

# Stats
r = G(tok, "/api/report-cards/stats/summary")
check("Report Cards", "Stats", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
end_module("Report Cards")

# ========== 16. CERTIFICATES MODULE ==========
start_module("Certificates")
r = G(tok, "/api/certificates")
check("Certificates", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
certificates = r.json() if r.status_code == 200 else []
check("Certificates", "Data Present", "PASS" if len(certificates) > 0 else "FAIL", f"{len(certificates)} certificates")

# Create
if students:
    stid = students[0]["id"]
    r = P(tok, "/api/certificates", j={"student_id": stid, "certificate_type": "Transfer", "remarks": "QA Test"})
    new_certid = r.json().get("id") if r.status_code in (200, 201) else None
    check("Certificates", "Create", "PASS" if new_certid else "FAIL", f"ID={new_certid}")

    if new_certid:
        r = G(tok, f"/api/certificates/{new_certid}")
        check("Certificates", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

        r = U(tok, f"/api/certificates/{new_certid}", j={"remarks": "QA Test Updated"})
        check("Certificates", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

        r = P(tok, "/api/certificates", j={})
        check("Certificates", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

        r = D(tok, f"/api/certificates/{new_certid}")
        check("Certificates", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Certificates")

# ========== 17. NOTICES MODULE ==========
start_module("Notices")
r = G(tok, "/api/notices")
check("Notices", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
notices = r.json() if r.status_code == 200 else []
check("Notices", "Data Present", "PASS" if len(notices) > 0 else "FAIL", f"{len(notices)} notices")

if notices:
    nid = notices[0]["id"]
    r = G(tok, f"/api/notices/{nid}")
    check("Notices", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
r = P(tok, "/api/notices", j={"title": "QA Notice", "content": "QA Test Notice", "target_roles": "Student,Parent"})
new_nid = r.json().get("id") if r.status_code in (200, 201) else None
check("Notices", "Create", "PASS" if new_nid else "FAIL", f"ID={new_nid}")

if new_nid:
    r = U(tok, f"/api/notices/{new_nid}", j={"title": "QA Notice Updated"})
    check("Notices", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Filter
r = G(tok, "/api/notices/filter", params={"target_role": "Student"})
check("Notices", "Filter", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/notices", j={})
check("Notices", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_nid:
    r = D(tok, f"/api/notices/{new_nid}")
    check("Notices", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Notices")

# ========== 18. EVENTS MODULE ==========
start_module("Events")
r = G(tok, "/api/events")
check("Events", "List", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
events = r.json() if r.status_code == 200 else []
check("Events", "Data Present", "PASS" if len(events) > 0 else "FAIL", f"{len(events)} events")

if events:
    evid = events[0]["id"]
    r = G(tok, f"/api/events/{evid}")
    check("Events", "Get Single", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Create
now = datetime.now()
r = P(tok, "/api/events", j={"title": "QA Event", "description": "QA Test Event", "start_date": now.isoformat(), "end_date": (now + timedelta(hours=2)).isoformat(), "event_type": "academic"})
new_evid = r.json().get("id") if r.status_code in (200, 201) else None
check("Events", "Create", "PASS" if new_evid else "FAIL", f"ID={new_evid}")

if new_evid:
    r = U(tok, f"/api/events/{new_evid}", j={"title": "QA Event Updated"})
    check("Events", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = P(tok, "/api/events", j={})
check("Events", "Form Validation", "PASS" if r.status_code in (400, 422) else "FAIL", f"{r.status_code}")

if new_evid:
    r = D(tok, f"/api/events/{new_evid}")
    check("Events", "Delete", "PASS" if r.status_code in (200, 204) else "FAIL", f"{r.status_code}")
end_module("Events")

# ========== 19. SETTINGS MODULE ==========
start_module("Settings")
r = G(tok, "/api/settings")
check("Settings", "Get", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

r = U(tok, "/api/settings", j={"school_name": "Greenwood International Academy"})
check("Settings", "Update", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Dashboard
r = G(tok, "/api/dashboard/summary")
check("Settings", "Dashboard", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Analytics
r = G(tok, "/api/analytics/overview")
check("Settings", "Analytics", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")

# Global search
r = G(tok, "/api/search", params={"q": "Aarav"})
check("Settings", "Global Search", "PASS" if r.status_code == 200 else "FAIL", f"{r.status_code}")
end_module("Settings")

# ========== SUMMARY ==========
print("\n" + "="*60)
print("FINAL QA SUMMARY")
print("="*60)

total_pass = 0
total_fail = 0
total_warn = 0
total_tests = 0

for mod, d in module_results.items():
    t = d["PASS"] + d["FAIL"] + d["WARN"]
    total_tests += t
    total_pass += d["PASS"]
    total_fail += d["FAIL"]
    total_warn += d["WARN"]
    status = "PASS" if d["FAIL"] == 0 else "FAIL"
    print(f"  {mod}: {t} tests | PASS={d['PASS']} FAIL={d['FAIL']} WARN={d['WARN']} | {status}")

print(f"\n  TOTAL: {total_tests} tests | PASS={total_pass} FAIL={total_fail} WARN={total_warn}")

# Save results
output = {
    "results": results,
    "summary": {
        "total": total_tests,
        "pass": total_pass,
        "fail": total_fail,
        "warn": total_warn,
        "modules_tested": len(module_results),
    }
}
with open("qa_comprehensive_results.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
print("\nResults saved to qa_comprehensive_results.json")