import requests

BASE = 'http://127.0.0.1:8001'

# Login as School Admin
r = requests.post(f'{BASE}/auth/token', data={'username': 'admin@springfield.edu', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test: call an erp.py endpoint that uses _apply_tenant_filter (which uses get_current_school_id)
# and a report_cards.py endpoint that uses get_current_school_id directly
# If both return data from school_id=1, the contextvar is working

# Students (erp.py) - uses _apply_tenant_filter
r = requests.get(f'{BASE}/api/students', headers=headers)
students = r.json()
print(f'Students (erp.py): {r.status_code} - {len(students)} found')
# Check if all have school_id=1
if students:
    school_ids = set(s.get("school_id", "?") for s in students)
    print(f'  school_ids: {school_ids}')

# Report Cards (report_cards.py) - uses get_current_school_id() directly
r = requests.get(f'{BASE}/api/report-cards', headers=headers)
rcs = r.json()
print(f'\nReport Cards (report_cards.py): {r.status_code} - {len(rcs)} found')
if rcs:
    school_ids = set(rc.get("school_id", "?") for rc in rcs)
    print(f'  school_ids: {school_ids}')

# Check if it's a contextvar propagation issue
# Let me try calling the generate endpoint which also uses get_current_school_id
r = requests.post(f'{BASE}/api/report-cards/generate', headers=headers, json={
    'student_id': 1, 'exam_id': 1, 'academic_year_id': 1
})
print(f'\nGenerate RC: {r.status_code}')
print(f'  Response: {r.text[:300]}')

# Check the verify endpoint (no auth needed)
r = requests.get(f'{BASE}/api/report-cards/verify/abcd', headers=headers)
print(f'\nVerify (nonexistent): {r.status_code}')
print(f'  Response: {r.text[:200]}')

# Test the settings endpoint
r = requests.get(f'{BASE}/api/settings', headers=headers)
print(f'\nSettings: {r.status_code}')
print(f'  Response: {r.text[:300]}')
