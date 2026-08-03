import requests

BASE = 'http://127.0.0.1:8001'

# Login
r = requests.post(f'{BASE}/auth/token', data={'username': 'admin@springfield.edu', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test users.py profile endpoint - this uses auth.get_current_user directly
r = requests.get(f'{BASE}/api/users', headers=headers, params={'limit': 100})
users = r.json() if r.ok else []
print(f'Users: {r.status_code} ({len(users)})')
if users:
    for u in users[:3]:
        print(f'  {u.get("email")} - school_id={u.get("school_id")} - role={u.get("role")}')

# Test erp.py endpoint that uses get_current_school_id
r = requests.get(f'{BASE}/api/rooms', headers=headers)
print(f'\nRooms: {r.status_code} ({len(r.json()) if r.ok else 0})')
if r.ok:
    for room in r.json():
        print(f'  {room.get("room_name")} - school_id={room.get("school_id")}')

# Test report_cards.py endpoint
r = requests.get(f'{BASE}/api/report-cards', headers=headers)
print(f'\nReport Cards: {r.status_code} ({len(r.json()) if r.ok else 0})')

# Check the settings endpoint error
r = requests.get(f'{BASE}/api/settings', headers=headers)
print(f'\nSettings: {r.status_code}')

# Check the erp.py students endpoint with a specific filter that would require school_id
r = requests.get(f'{BASE}/api/fee-structures', headers=headers)
print(f'Fee Structures: {r.status_code} ({len(r.json()) if r.ok else 0})')
