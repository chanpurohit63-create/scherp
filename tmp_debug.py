import requests

BASE = 'http://127.0.0.1:8001'

# Login as Super Admin
r = requests.post(f'{BASE}/auth/token', data={'username': 'superadmin@springfield.edu', 'password': 'admin123'})
print(f'Login: {r.status_code}')
sa_token = r.json()['access_token']
sa_headers = {'Authorization': f'Bearer {sa_token}'}

# Create School - print full response
r = requests.post(f'{BASE}/api/superadmin/schools', headers=sa_headers, json={
    'school_name': 'Greenfield Elementary', 'school_code': 'GE002', 'email': 'info@greenfield.edu',
    'phone': '555-0200', 'address': '456 Oak St', 'city': 'Greenfield', 'state': 'IL',
    'principal_name': 'Dr. John Doe', 'subscription_plan': 'premium'
})
print(f'Create School: {r.status_code}')
print(f'Response: {r.text[:500]}')

# List schools
r = requests.get(f'{BASE}/api/superadmin/schools', headers=sa_headers)
print(f'List Schools: {r.status_code} ({len(r.json())} schools)')

# Test report card list
r = requests.get(f'{BASE}/api/report-cards', headers=sa_headers)
print(f'List Report Cards: {r.status_code} ({len(r.json()) if r.ok else r.text[:200]})')

if r.ok and r.json():
    rc = r.json()[0]
    print(f'First RC: id={rc["id"]}, status={rc.get("status", "N/A")}, class_id={rc.get("class_id", "N/A")}')
    
    # Test publish
    r2 = requests.post(f'{BASE}/api/report-cards/{rc["id"]}/publish', headers=sa_headers)
    print(f'Publish: {r2.status_code}')
    
    # Test archive
    r3 = requests.post(f'{BASE}/api/report-cards/{rc["id"]}/archive', headers=sa_headers)
    print(f'Archive: {r3.status_code}')
    
    # Test PDF
    r4 = requests.get(f'{BASE}/api/report-cards/{rc["id"]}/pdf', headers=sa_headers)
    print(f'PDF: {r4.status_code} ({len(r4.content)} bytes)')
    
    # Test verify
    r5 = requests.get(f'{BASE}/api/report-cards/verify/{rc["verification_id"]}')
    print(f'Verify: {r5.status_code} ({r5.json().get("valid", "FAIL")})')
    
    # Test stats
    r6 = requests.get(f'{BASE}/api/report-cards/stats/summary', headers=sa_headers)
    print(f'Stats: {r6.status_code}')

# Test generate
r = requests.post(f'{BASE}/api/report-cards/generate', headers=sa_headers, json={
    'student_id': 1, 'exam_id': 1, 'academic_year_id': 1
})
print(f'Generate: {r.status_code} ({r.text[:200] if not r.ok else "OK"})')

# Test search
r = requests.get(f'{BASE}/api/search', headers=sa_headers, params={'q': 'Alice'})
print(f'Search: {r.status_code}')

# Test notifications
r = requests.get(f'{BASE}/api/notifications/unread', headers=sa_headers)
print(f'Unread: {r.status_code} ({r.json()})')

# Test settings
r = requests.get(f'{BASE}/api/settings', headers=sa_headers)
print(f'Settings: {r.status_code} ({r.json().get("school_name", "FAIL") if r.ok else r.text[:100]})')

print('\n=== DONE ===')
