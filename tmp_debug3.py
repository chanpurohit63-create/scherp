import requests, json

BASE = 'http://127.0.0.1:8001'

# Login as School Admin
r = requests.post(f'{BASE}/auth/token', data={'username': 'admin@springfield.edu', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test report cards list with verbose output
r = requests.get(f'{BASE}/api/report-cards', headers=headers)
print(f'List RC: {r.status_code}')
print(f'  Response: {r.text[:500]}')

# Test settings with verbose output
r = requests.get(f'{BASE}/api/settings', headers=headers)
print(f'\nSettings: {r.status_code}')
print(f'  Response: {r.text[:500]}')

# Test student profile
r = requests.get(f'{BASE}/api/students/1/profile', headers=headers)
print(f'\nStudent Profile: {r.status_code}')
print(f'  Response: {r.text[:300]}')

# Test generate report card
r = requests.post(f'{BASE}/api/report-cards/generate', headers=headers, json={
    'student_id': 1, 'exam_id': 1, 'academic_year_id': 1
})
print(f'\nGenerate RC: {r.status_code}')
print(f'  Response: {r.text[:300]}')

# Test dashboard
r = requests.get(f'{BASE}/api/dashboard/summary', headers=headers)
print(f'\nDashboard: {r.status_code}')
print(f'  Response: {r.text[:300]}')

# Test notifications unread
r = requests.get(f'{BASE}/api/notifications/unread', headers=headers)
print(f'\nUnread: {r.status_code}')
print(f'  Response: {r.text[:200]}')
