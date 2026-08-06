import requests

BASE = "http://127.0.0.1:8000"
credential_sets = [
    # (email, password, label)
    ("teacher1@testalpha.edu", "TeacherPass123!", "Teacher1 (e2e_full)"),
    ("teacher2@testalpha.edu", "TeacherPass123!", "Teacher2 (e2e_full)"),
    ("student_stu001@testalpha.edu", "StudentPass123!", "Student001 (e2e_full)"),
    ("john.anderson@email.com", "ParentPass123!", "Parent John (e2e_full)"),
    ("schooladmin@testalpha.edu", "AdminPass123!", "SchoolAdmin Alpha (e2e_full)"),
    ("schooladmin@testalpha.edu", "NewAdminPass456!", "SchoolAdmin Alpha changed (e2e_full)"),
    ("teacher1@testalpha.edu", "admin123", "Teacher1 (default pw)"),
    ("student_stu001@testalpha.edu", "admin123", "Student001 (default pw)"),
    ("john.anderson@email.com", "admin123", "Parent John (default pw)"),
]

for email, pw, label in credential_sets:
    try:
        r = requests.post(f"{BASE}/auth/token", data={"username": email, "password": pw}, timeout=10)
        print(f"{label} | {email} | {pw} -> {r.status_code} {r.text[:80]}")
    except Exception as e:
        print(f"{label} | {email} -> ERROR {e}")