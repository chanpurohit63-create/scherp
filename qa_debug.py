"""Debug the QA failures"""
import requests, json

BASE = "http://localhost:8000"

def login(email, pw):
    r = requests.post(f"{BASE}/auth/token", data={"username": email, "password": pw})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

def H(tok): return {"Authorization": f"Bearer {tok}"}

# Login
sa = login("admin@school.local", "admin123")
sat = login("admin@greenwood.edu", "NewGreenwood@2026")
if not sat:
    sat = login("admin@greenwood.edu", "Greenwood@2026")

print("=== 1. Parents Update (405) ===")
r = requests.get(f"{BASE}/api/parents", headers=H(sat))
parents = r.json() if r.status_code == 200 else []
if parents:
    pid = parents[0]["id"]
    r = requests.put(f"{BASE}/api/parents/{pid}", headers=H(sat), json={"phone": "555-5678"})
    print(f"  PUT /api/parents/{pid}: {r.status_code}")
    print(f"  Response: {r.text[:200]}")

print("\n=== 2. Timetable Create ===")
r = requests.get(f"{BASE}/api/classes", headers=H(sat))
classes = r.json() if r.status_code == 200 else []
r = requests.get(f"{BASE}/api/subjects", headers=H(sat))
subjects = r.json() if r.status_code == 200 else []
r = requests.get(f"{BASE}/api/teachers", headers=H(sat))
teachers = r.json() if r.status_code == 200 else []
r = requests.get(f"{BASE}/api/academic-years", headers=H(sat))
years = r.json() if r.status_code == 200 else []

print(f"  Classes: {len(classes)}, Subjects: {len(subjects)}, Teachers: {len(teachers)}, Years: {len(years)}")
if classes and subjects and teachers and years:
    cid = classes[0]["id"]
    subid = subjects[0]["id"]
    tid = teachers[0]["id"]
    ayid = years[0]["id"]
    print(f"  Using class={cid}, subject={subid}, teacher={tid}, year={ayid}")
    payload = {"class_id": cid, "subject_id": subid, "teacher_id": tid, "day_of_week": 0, "period": 1, "start_time": "09:00", "end_time": "09:45", "academic_year_id": ayid}
    r = requests.post(f"{BASE}/api/timetable", headers=H(sat), json=payload)
    print(f"  POST /api/timetable: {r.status_code}")
    print(f"  Response: {r.text[:500]}")

print("\n=== 3. Notices Filter (422) ===")
r = requests.get(f"{BASE}/api/notices/filter", headers=H(sat), params={"target_role": "Student"})
print(f"  GET /api/notices/filter?target_role=Student: {r.status_code}")
print(f"  Response: {r.text[:500]}")

print("\n=== 4. Report Card Generate (404) ===")
r = requests.get(f"{BASE}/api/students", headers=H(sat))
students = r.json() if r.status_code == 200 else []
r = requests.get(f"{BASE}/api/exams", headers=H(sat))
exams = r.json() if r.status_code == 200 else []
r = requests.get(f"{BASE}/api/academic-years", headers=H(sat))
years = r.json() if r.status_code == 200 else []
print(f"  Students: {len(students)}, Exams: {len(exams)}, Years: {len(years)}")
if students and exams and years:
    stid = students[0]["id"]
    exid = exams[0]["id"]
    ayid = years[0]["id"]
    print(f"  Using student={stid}, exam={exid}, year={ayid}")
    r = requests.post(f"{BASE}/api/report-cards/generate", headers=H(sat), json={"student_id": stid, "exam_id": exid, "academic_year_id": ayid})
    print(f"  POST /api/report-cards/generate: {r.status_code}")
    print(f"  Response: {r.text[:500]}")