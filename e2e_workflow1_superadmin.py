"""
WORKFLOW 1: Super Admin (Company)
- Login as Super Admin
- Dashboard
- School creation
- School editing
- Subscription
- Suspend
- Activate
- Reset password
- Search
- Filters
- Pagination
"""
import requests
import json
import sys
from datetime import date, timedelta

BASE = "http://localhost:8000"
results = []

def log(test_name, status, detail=""):
    emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠"
    results.append((test_name, status, detail))
    print(f"{emoji} {test_name}: {detail}")

def login(email, password):
    """Login via OAuth2 password flow"""
    resp = requests.post(f"{BASE}/auth/token", data={
        "username": email,
        "password": password,
    })
    return resp

# ============================================================
# STEP 1: Login as Super Admin
# ============================================================
print("\n" + "="*60)
print("WORKFLOW 1: SUPER ADMIN")
print("="*60)

resp = login("admin@school.local", "admin123")
if resp.status_code == 200:
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    log("Super Admin Login", "PASS", f"Got token (status {resp.status_code})")
else:
    log("Super Admin Login", "FAIL", f"Status {resp.status_code}: {resp.text}")
    sys.exit(1)

# ============================================================
# STEP 2: Verify user info
# ============================================================
resp = requests.get(f"{BASE}/users/me", headers=headers)
if resp.status_code == 200:
    user = resp.json()
    log("Get Current User (/users/me)", "PASS", f"Role: {user.get('role')}, Name: {user.get('full_name')}")
else:
    log("Get Current User (/users/me)", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 3: Super Admin Dashboard
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/platform/dashboard", headers=headers)
if resp.status_code == 200:
    dashboard = resp.json()
    log("Super Admin Dashboard", "PASS", f"Data: {json.dumps(dashboard)[:200]}")
else:
    log("Super Admin Dashboard", "FAIL", f"Status {resp.status_code}: {resp.text}")

# Platform analytics
resp = requests.get(f"{BASE}/api/superadmin/platform/analytics", headers=headers)
if resp.status_code == 200:
    log("Platform Analytics", "PASS", f"Data: {json.dumps(resp.json())[:200]}")
else:
    log("Platform Analytics", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 4: List existing schools
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/schools", headers=headers)
if resp.status_code == 200:
    schools = resp.json()
    if isinstance(schools, list):
        log("List Schools", "PASS", f"Found {len(schools)} schools")
    elif isinstance(schools, dict) and "items" in schools:
        log("List Schools", "PASS", f"Found {len(schools['items'])} schools (paginated)")
    else:
        log("List Schools", "PASS", f"Response type: {type(schools)}, data: {str(schools)[:200]}")
else:
    log("List Schools", "FAIL", f"Status {resp.status_code}: {resp.text}")

# School count
resp = requests.get(f"{BASE}/api/superadmin/schools/count", headers=headers)
if resp.status_code == 200:
    log("School Count", "PASS", f"Count: {resp.json()}")
else:
    log("School Count", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 5: Create a brand-new school (with admin account)
# ============================================================
new_school_data = {
    "school_name": "Greenwood International School",
    "school_code": "GIS2026",
    "email": "info@greenwood.edu",
    "phone": "555-0100",
    "address": "123 Education Lane",
    "subscription_plan": "premium",
}

resp = requests.post(f"{BASE}/api/superadmin/schools", json=new_school_data, headers=headers)
if resp.status_code in (200, 201):
    new_school = resp.json()
    new_school_id = new_school.get("id")
    log("Create School", "PASS", f"Created school ID={new_school_id}, name={new_school.get('school_name')}")
else:
    log("Create School", "FAIL", f"Status {resp.status_code}: {resp.text}")
    # Try to find existing school
    resp2 = requests.get(f"{BASE}/api/superadmin/schools", headers=headers)
    if resp2.status_code == 200:
        data = resp2.json()
        school_list = data if isinstance(data, list) else data.get("items", [])
        for s in school_list:
            if s.get("school_code") == "GIS2026":
                new_school_id = s["id"]
                log("Create School (found existing)", "PASS", f"Using existing school ID={new_school_id}")
                break
        else:
            new_school_id = None
    else:
        new_school_id = None

if not new_school_id:
    print("ERROR: Cannot proceed without a school ID")
    sys.exit(1)

# Create admin user for the school (as the UI does)
admin_email = "admin@greenwood.edu"
admin_password = "Greenwood@2026"
admin_name = "John Smith"
register_data = {
    "email": admin_email,
    "password": admin_password,
    "full_name": admin_name,
    "role": "School Admin",
}
resp = requests.post(f"{BASE}/auth/register?school_id={new_school_id}", json=register_data, headers=headers)
if resp.status_code in (200, 201):
    log("Create School Admin User", "PASS", f"Admin: {admin_email}")
else:
    # Maybe already exists
    if "already" in resp.text.lower() or "exists" in resp.text.lower():
        log("Create School Admin User", "PASS", f"Admin already exists: {admin_email}")
    else:
        log("Create School Admin User", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 6: Get school details
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/schools/{new_school_id}", headers=headers)
if resp.status_code == 200:
    school_detail = resp.json()
    log("Get School Details", "PASS", f"Name: {school_detail.get('school_name')}, Code: {school_detail.get('school_code')}")
else:
    log("Get School Details", "FAIL", f"Status {resp.status_code}: {resp.text}")

# School statistics
resp = requests.get(f"{BASE}/api/superadmin/schools/{new_school_id}/statistics", headers=headers)
if resp.status_code == 200:
    log("School Statistics", "PASS", f"Data: {json.dumps(resp.json())[:200]}")
else:
    log("School Statistics", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 7: Edit school
# ============================================================
edit_data = {
    "school_name": "Greenwood International Academy",
    "principal_name": "Dr. Sarah J. Mitchell",
    "phone": "555-0101",
}
resp = requests.put(f"{BASE}/api/superadmin/schools/{new_school_id}", json=edit_data, headers=headers)
if resp.status_code == 200:
    edited = resp.json()
    if edited.get("school_name") == "Greenwood International Academy":
        log("Edit School", "PASS", f"Updated name to: {edited.get('school_name')}")
    else:
        log("Edit School", "PARTIAL", f"Response: {json.dumps(edited)[:200]}")
else:
    log("Edit School", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 8: Subscription management
# ============================================================
# Subscription info is part of the school object (no separate GET endpoint)
resp = requests.get(f"{BASE}/api/superadmin/schools/{new_school_id}", headers=headers)
if resp.status_code == 200:
    school_data = resp.json()
    log("Get Subscription (from school)", "PASS", f"Plan: {school_data.get('subscription_plan')}, Start: {school_data.get('subscription_start')}, End: {school_data.get('subscription_end')}")
else:
    log("Get Subscription (from school)", "FAIL", f"Status {resp.status_code}: {resp.text}")

# Update subscription (uses query params: plan, subscription_start, subscription_end)
sub_params = {
    "plan": "enterprise",
    "subscription_start": str(date.today()),
    "subscription_end": str(date.today() + timedelta(days=730)),
}
resp = requests.put(f"{BASE}/api/superadmin/schools/{new_school_id}/subscription", params=sub_params, headers=headers)
if resp.status_code == 200:
    updated = resp.json()
    if updated.get("subscription_plan") == "enterprise":
        log("Update Subscription", "PASS", f"Updated to enterprise plan, student_limit={updated.get('student_limit')}")
    else:
        log("Update Subscription", "PARTIAL", f"Response: {json.dumps(updated)[:200]}")
else:
    log("Update Subscription", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 9: Suspend school
# ============================================================
resp = requests.post(f"{BASE}/api/superadmin/schools/{new_school_id}/suspend", headers=headers)
if resp.status_code == 200:
    log("Suspend School", "PASS", f"School suspended")
else:
    log("Suspend School", "FAIL", f"Status {resp.status_code}: {resp.text}")

# Verify suspended
resp = requests.get(f"{BASE}/api/superadmin/schools/{new_school_id}", headers=headers)
if resp.status_code == 200:
    status = resp.json().get("status")
    if status == "suspended":
        log("Verify Suspended Status", "PASS", f"Status is '{status}'")
    else:
        log("Verify Suspended Status", "PARTIAL", f"Status is '{status}' (expected 'suspended')")
else:
    log("Verify Suspended Status", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 10: Activate school
# ============================================================
resp = requests.post(f"{BASE}/api/superadmin/schools/{new_school_id}/activate", headers=headers)
if resp.status_code == 200:
    log("Activate School", "PASS", f"School activated")
else:
    log("Activate School", "FAIL", f"Status {resp.status_code}: {resp.text}")

# Verify active
resp = requests.get(f"{BASE}/api/superadmin/schools/{new_school_id}", headers=headers)
if resp.status_code == 200:
    status = resp.json().get("status")
    if status == "active":
        log("Verify Active Status", "PASS", f"Status is '{status}'")
    else:
        log("Verify Active Status", "PARTIAL", f"Status is '{status}' (expected 'active')")
else:
    log("Verify Active Status", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 11: Reset admin password (uses query param: new_password)
# ============================================================
reset_new_password = "NewGreenwood@2026"
resp = requests.post(f"{BASE}/api/superadmin/schools/{new_school_id}/reset-admin-password", params={"new_password": reset_new_password}, headers=headers)
if resp.status_code == 200:
    log("Reset Admin Password", "PASS", f"Password reset to: {reset_new_password}")
    new_admin_password = reset_new_password
    new_admin_email = admin_email
    print(f"   -> Admin email: {new_admin_email}, new password: {new_admin_password}")
else:
    log("Reset Admin Password", "FAIL", f"Status {resp.status_code}: {resp.text}")
    new_admin_password = admin_password
    new_admin_email = admin_email

# ============================================================
# STEP 12: Search
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/schools?search=Greenwood", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list):
        found = [s for s in data if "Greenwood" in s.get("school_name", "")]
    elif isinstance(data, dict) and "items" in data:
        found = [s for s in data["items"] if "Greenwood" in s.get("school_name", "")]
    else:
        found = []
    if found:
        log("Search Schools (by name)", "PASS", f"Found {len(found)} matching 'Greenwood'")
    else:
        log("Search Schools (by name)", "PARTIAL", f"Search returned but no match. Data: {str(data)[:200]}")
else:
    log("Search Schools (by name)", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 13: Filters
# ============================================================
# Filter by status
resp = requests.get(f"{BASE}/api/superadmin/schools?status_filter=active", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list):
        count = len(data)
    elif isinstance(data, dict) and "items" in data:
        count = len(data["items"])
    else:
        count = 0
    log("Filter Schools (status=active)", "PASS", f"Found {count} active schools")
else:
    log("Filter Schools (status=active)", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 14: Pagination (client-side in UI, API uses skip/limit)
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/schools?skip=0&limit=2", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list):
        log("Pagination (skip=0, limit=2)", "PASS", f"Got {len(data)} schools (API uses skip/limit)")
    elif isinstance(data, dict) and "items" in data:
        log("Pagination (skip=0, limit=2)", "PASS", f"Items: {len(data['items'])}")
    else:
        log("Pagination (skip=0, limit=2)", "PARTIAL", f"Unexpected format: {str(data)[:200]}")
else:
    log("Pagination (skip=0, limit=2)", "FAIL", f"Status {resp.status_code}: {resp.text}")

# Page 2
resp = requests.get(f"{BASE}/api/superadmin/schools?skip=2&limit=2", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list):
        log("Pagination (skip=2, limit=2)", "PASS", f"Got {len(data)} schools")
    elif isinstance(data, dict) and "items" in data:
        log("Pagination (skip=2, limit=2)", "PASS", f"Items: {len(data['items'])}")
    else:
        log("Pagination (skip=2, limit=2)", "PARTIAL", f"Unexpected format: {str(data)[:200]}")
else:
    log("Pagination (skip=2, limit=2)", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 15: Audit logs
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/audit-logs", headers=headers)
if resp.status_code == 200:
    log("Audit Logs", "PASS", f"Data: {str(resp.json())[:200]}")
else:
    log("Audit Logs", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# STEP 16: Subscription plans
# ============================================================
resp = requests.get(f"{BASE}/api/superadmin/subscriptions/plans", headers=headers)
if resp.status_code == 200:
    log("Subscription Plans", "PASS", f"Data: {str(resp.json())[:200]}")
else:
    log("Subscription Plans", "FAIL", f"Status {resp.status_code}: {resp.text}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("WORKFLOW 1 SUMMARY")
print("="*60)
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
partial = sum(1 for _, s, _ in results if s == "PARTIAL")
print(f"Total: {len(results)} | ✅ Passed: {passed} | ❌ Failed: {failed} | ⚠ Partial: {partial}")

# Save school ID and admin credentials for next workflows
output = {
    "school_id": new_school_id,
    "admin_email": new_admin_email,
    "admin_password": new_admin_password,
    "results": [{"test": t, "status": s, "detail": d} for t, s, d in results],
}
with open("workflow1_results.json", "w") as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nSchool ID: {new_school_id}")
print(f"Admin Email: {new_admin_email}")
print(f"Admin Password: {new_admin_password}")
print("Results saved to workflow1_results.json")