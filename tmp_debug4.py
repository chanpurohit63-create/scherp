import requests

BASE = 'http://127.0.0.1:8001'

# Login as School Admin
r = requests.post(f'{BASE}/auth/token', data={'username': 'admin@springfield.edu', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Check users/me (which uses auth.get_current_user)
r = requests.get(f'{BASE}/users/me', headers=headers)
print(f'Users/me: {r.status_code}')
print(f'  Response: {r.json()}')

# Check students (which uses auth.get_current_user + tenant filter)
r = requests.get(f'{BASE}/api/students', headers=headers)
print(f'\nStudents: {r.status_code} ({len(r.json()) if r.ok else 0})')

# Check classes
r = requests.get(f'{BASE}/api/classes', headers=headers)
print(f'Classes: {r.status_code} ({len(r.json()) if r.ok else 0})')

# Check exam-results (uses auth.get_current_user)
r = requests.get(f'{BASE}/api/exam-results', headers=headers)
print(f'\nExam Results: {r.status_code} ({len(r.json()) if r.ok else 0})')

# Check report cards
r = requests.get(f'{BASE}/api/report-cards', headers=headers)
print(f'Report Cards: {r.status_code} ({len(r.json()) if r.ok else 0})')
if r.ok:
    print(f'  Data: {r.text[:200]}')

# Check if the issue is with the report_cards router's get_current_school_id
# Let me check the raw endpoint without response_model
import json
r = requests.get(f'{BASE}/api/report-cards/stats/summary', headers=headers)
print(f'\nStats Summary: {r.status_code}')
print(f'  Response: {r.text[:300]}')
