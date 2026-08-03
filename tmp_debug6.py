import requests
from jose import jwt as jose_jwt

BASE = 'http://127.0.0.1:8001'

# Login
r = requests.post(f'{BASE}/auth/token', data={'username': 'admin@springfield.edu', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Decode token to check school_id
payload = jose_jwt.decode(token, 'dev-secret-key', algorithms=['HS256'])
print(f'Token school_id: {payload.get("school_id")}')
print(f'Token user_id: {payload.get("user_id")}')
print(f'Token role: {payload.get("role")}')

# Test a few erp.py endpoints that should use tenant filtering
# If get_current_school_id returns None, erp.py would return ALL data (unfiltered)
# Let me check fee-assignments which should only return for this school
r = requests.get(f'{BASE}/api/fee-assignments', headers=headers, params={'limit': 100})
print(f'\nFee Assignments: {r.status_code} ({len(r.json()) if r.ok else 0})')
if r.ok and r.json():
    ids = [fa.get("id") for fa in r.json()]
    print(f'  IDs: {ids}')

# Check payments
r = requests.get(f'{BASE}/api/payments', headers=headers, params={'limit': 100})
print(f'\nPayments: {r.status_code} ({len(r.json()) if r.ok else 0})')

# Check the report_cards.py list endpoint
r = requests.get(f'{BASE}/api/report-cards', headers=headers)
print(f'\nReport Cards: {r.status_code}')
if r.ok:
    data = r.json()
    print(f'  Count: {len(data)}')
    if data:
        print(f'  First: {data[0]}')

# Check generate report card with different student_id
for sid in [1, 2, 3, 12, 15]:
    r = requests.post(f'{BASE}/api/report-cards/generate', headers=headers, json={
        'student_id': sid, 'exam_id': 1, 'academic_year_id': 1
    })
    print(f'Generate RC for student {sid}: {r.status_code} ({r.json().get("detail", "OK") if r.ok else r.json().get("detail", r.text[:100])})')
