"""
End-to-end ERP test harness - exercises the ERP exactly as a real school would.
Uses the live REST API (same endpoints the React frontend calls).
"""
import requests
import json
import sys
import traceback

BASE = "http://127.0.0.1:8000"
results = []
current_step = ""

def log(step, name, expected, actual, ok, err=None, root_cause=None, fix=None):
    results.append({
        "step": step,
        "name": name,
        "expected": expected,
        "actual": actual,
        "ok": ok,
        "error": err,
        "root_cause": root_cause,
        "fix": fix,
    })
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {step} | {name}")
    if not ok:
        print(f"    Expected: {expected}")
        print(f"    Actual: {actual}")
        if err:
            print(f"    Error: {err}")
        if root_cause:
            print(f"    Root Cause: {root_cause}")
        if fix:
            print(f"    Fix: {fix}")

def req(method, path, token=None, json_body=None, files=None, expect_status=200):
    """Make an HTTP request and return (status, body, error)."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{path}", headers=headers, timeout=30)
        elif method == "POST":
            if files:
                r = requests.post(f"{BASE}{path}", headers=headers, files=files, timeout=60)
            else:
                r = requests.post(f"{BASE}{path}", headers=headers, json=json_body, timeout=30)
        elif method == "PUT":
            r = requests.put(f"{BASE}{path}", headers=headers, json=json_body, timeout=30)
        elif method == "DELETE":
            r = requests.delete(f"{BASE}{path}", headers=headers, timeout=30)
        else:
            return None, None, "Unsupported method"
        try:
            body = r.json()
        except Exception:
            body = r.text
        return r.status_code, body, None
    except Exception as e:
        return None, None, str(e)

def login(email, password):
    """Login and return token."""
    r = requests.post(f"{BASE}/auth/token", data={"username": email, "password": password}, timeout=30)
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

# =====================================================================
# STEP 1 - SUPER ADMIN
# =====================================================================
print("=" * 80)
print("STEP 1 - SUPER ADMIN")
print("=" * 80)

# 1.1 Login as Super Admin
token = login("admin@school.local", "admin123")
log("1.1", "Super Admin login", "Token returned", f"Token {'returned' if token else 'FAILED'}", token is not None,
    err="Login returned non-200" if token is None else None)

if token:
    # 1.2 Dashboard loads
    status, body, err = req("GET", "/api/superadmin/platform/dashboard", token)
    log("1.2", "Super Admin dashboard loads", "200 + dashboard data", f"{status}", status == 200,
        err=str(err) if err else (str(body) if status != 200 else None))

    # 1.3 Create a new school
    school_data = {
        "school_name": "Test School Alpha",
        "school_code": "TSA002",
        "address": "123 Test St",
        "phone": "555-1234",
        "email": "info@testalpha.edu",
        "subscription_plan": "premium",
    }
    status, body, err = req("POST", "/api/superadmin/schools", token, school_data, expect_status=201)
    school_created = status == 201 and body.get("id")
    log("1.3", "Create new school", "201 + school id", f"{status} id={body.get('id') if isinstance(body, dict) else 'N/A'}", school_created,
        err=str(err) if err else (str(body) if not school_created else None))
    school_id = body.get("id") if school_created else None

    if school_created:
        # 1.4 School appears in list
        status, body, err = req("GET", f"/api/superadmin/schools?search=Test School Alpha", token)
        in_list = status == 200 and any(s.get("school_name") == "Test School Alpha" for s in body)
        log("1.4", "School appears in list", "School in list", f"in_list={in_list}", in_list,
            err=str(err) if err else (str(body) if not in_list else None))

        # 1.5 Edit school
        status, body, err = req("PUT", f"/api/superadmin/schools/{school_id}", token, {"school_name": "Test School Alpha (Updated)"})
        edit_ok = status == 200 and body.get("school_name") == "Test School Alpha (Updated)"
        log("1.5", "Edit school", "200 + updated name", f"{status} name={body.get('school_name') if isinstance(body, dict) else 'N/A'}", edit_ok,
            err=str(err) if err else (str(body) if not edit_ok else None))

        # 1.6 Search works
        status, body, err = req("GET", f"/api/superadmin/schools?search=Updated", token)
        search_ok = status == 200 and len(body) > 0
        log("1.6", "Search school", "Matching school returned", f"search results={len(body) if isinstance(body, list) else 'err'}", search_ok,
            err=str(err) if err else (str(body) if not search_ok else None))

        # 1.7 Filter works
        status, body, err = req("GET", f"/api/superadmin/schools?status_filter=active", token)
        filter_ok = status == 200 and all(s.get("status") == "active" for s in body)
        log("1.7", "Filter schools by status=active", "All schools active", f"status={status} count={len(body) if isinstance(body, list) else 'err'}", filter_ok,
            err=str(err) if err else (str(body) if not filter_ok else None))

        # 1.8 Suspend works
        status, body, err = req("POST", f"/api/superadmin/schools/{school_id}/suspend", token, {})
        suspend_ok = status == 200 and body.get("status") == "suspended"
        log("1.8", "Suspend school", "200 + status=suspended", f"{status} status={body.get('status') if isinstance(body, dict) else 'N/A'}", suspend_ok,
            err=str(err) if err else (str(body) if not suspend_ok else None))

        # 1.9 Activate works (reactivate for testing)
        status, body, err = req("POST", f"/api/superadmin/schools/{school_id}/activate", token, {})
        activate_ok = status == 200 and body.get("status") == "active"
        log("1.9", "Activate school", "200 + status=active", f"{status} status={body.get('status') if isinstance(body, dict) else 'N/A'}", activate_ok,
            err=str(err) if err else (str(body) if not activate_ok else None))

        # 1.10 Register School Admin credentials
        admin_email = "schooladmin@testalpha.edu"
        admin_pass = "AdminPass123!"
        status, body, err = req("POST", f"/auth/register?school_id={school_id}", None, {
            "email": admin_email,
            "password": admin_pass,
            "full_name": "Test Alpha Admin",
            "role": "School Admin",
        })
        admin_created = status == 200 and body.get("id")
        log("1.10", "School Admin credentials generated", "200 + admin user id", f"{status} admin_id={body.get('id') if isinstance(body, dict) else 'N/A'}", admin_created,
            err=str(err) if err else (str(body) if not admin_created else None))

        # 1.11 Verify admin can login
        admin_token = login(admin_email, admin_pass)
        log("1.11", "School Admin can login with generated credentials", "Token returned", f"Token {'returned' if admin_token else 'FAILED'}", admin_token is not None,
            err="Admin login failed" if not admin_token else None)

# Save results
with open("e2e_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results to e2e_results.json")