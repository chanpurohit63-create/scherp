import requests
from jose import jwt as jose_jwt
from app import models
from app.database import engine
from sqlmodel import Session, select

BASE = 'http://127.0.0.1:8001'

# Login
r = requests.post(f'{BASE}/auth/token', data={'username': 'admin@springfield.edu', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Check token payload
payload = jose_jwt.decode(token, 'dev-secret-key', algorithms=['HS256'])
print('Token payload:', {k: v for k, v in payload.items() if k != 'exp'})

# Check students via API
r = requests.get(f'{BASE}/api/students', headers=headers, params={'limit': 100})
print(f'Students API: {r.status_code}')
if r.ok:
    students = r.json()
    print(f'  Count: {len(students)}')
    if students:
        print(f'  First student id: {students[0].get("id")}')

# Check DB directly
with Session(engine) as session:
    rcs = session.exec(select(models.ReportCard).where(models.ReportCard.school_id == 1)).all()
    print(f'\nReport cards in DB (school_id=1): {len(rcs)}')
    for rc in rcs:
        print(f'  RC ID={rc.id}, student_id={rc.student_id}, school_id={rc.school_id}, status={rc.status}')

    students_db = session.exec(select(models.Student).where(models.Student.school_id == 1)).all()
    print(f'\nStudents in DB (school_id=1): {len(students_db)}')
    for s in students_db[:3]:
        print(f'  Student ID={s.id}, user_id={s.user_id}, admission_no={s.admission_no}')

    # Check what get_current_school_id returns
    from app.tenant import get_current_school_id
    print(f'\nget_current_school_id() (outside request): {get_current_school_id()}')

# Check settings endpoint
r = requests.get(f'{BASE}/api/settings', headers=headers)
print(f'\nSettings: {r.status_code}')
if not r.ok:
    print(f'  Error: {r.text[:500]}')
