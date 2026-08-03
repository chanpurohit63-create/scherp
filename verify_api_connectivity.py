"""Systematically verify frontend-backend API connectivity.

Extracts backend routes from all routers and frontend API calls from
all pages/components, then cross-references them to find broken links.
"""
import os
import re
import sys
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend", "src")


# ---------------------------------------------------------------------------
# 1. Extract backend routes
# ---------------------------------------------------------------------------
def extract_backend_routes():
    """Parse all router files, return list of {method, path}."""
    routes = []
    router_files = [
        "backend/app/routers/users.py",
        "backend/app/routers/erp.py",
        "backend/app/routers/notifications.py",
        "backend/app/routers/superadmin.py",
        "backend/app/routers/timetable.py",
        "backend/app/routers/report_cards.py",
        "backend/app/main.py",
    ]
    for rf in router_files:
        path = os.path.join(ROOT, rf)
        if not os.path.exists(path):
            print(f"WARN: route file not found: {rf}")
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        # @router.get("/path", ...) or @app.post("/path"...)
        pattern = re.compile(
            r"@(?:router|app)\.(get|post|put|delete|websocket)\("
            r"(?P<path>['\"][^'\"]+['\"])",
        )
        for m in pattern.finditer(content):
            method = m.group(1).upper()
            path_str = m.group(2).strip("'\"")
            routes.append({"method": method, "path": path_str, "file": rf})

    # Deduplicate
    seen = set()
    unique = []
    for r in routes:
        key = (r["method"], r["path"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


# ---------------------------------------------------------------------------
# 2. Extract frontend API calls
# ---------------------------------------------------------------------------
def extract_frontend_calls():
    """Scan all frontend .jsx/.js files for API path literals.

    We look for:
      - listResources(token, 'path', query)
      - createResource(token, 'path', body)
      - updateResource(token, 'path', id, body)
      - deleteResource(token, 'path', id)
      - postResource(token, 'path', body)
      - getResource(token, 'path', id)
      - uploadFile(token, 'path', file)
      - downloadFile(token, 'path', filename)
      - direct fetch(`${BACKEND_URL}/api/...`)
      - direct fetch(`${BACKEND_URL}/...`)
      - api function wrappers like listReportCards(...), generateReportCard(...)
    """
    calls = []
    call_patterns = [
        re.compile(r"\b(?:listResources|createResource|updateResource|deleteResource|"
                   r"postResource|getResource|uploadFile|downloadFile|fetchText)\s*\(\s*[^,]+,\s*"
                   r"['\"`]([^'\"`]+)['\"`]"),
        re.compile(r"(?:listResources|createResource|updateResource|deleteResource|"
                   r"postResource|getResource|uploadFile|downloadFile|fetchText)\s*\(\s*token\s*,\s*"
                   r"['\"`]([^'\"`]+)['\"`]"),
        re.compile(r"`\$\{BACKEND_URL\}/api/([^`'\"\s}\?]+)"),
        re.compile(r"`\$\{BACKEND_URL\}/([^`'\"\s}\?]+)"),
        re.compile(r"['\"]/api/([^'\"\s}\?]+)"),
    ]
    skip_dirs = {"node_modules", "dist", "build"}
    for dirpath, dirnames, filenames in os.walk(FRONTEND_DIR):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if not (fn.endswith(".jsx") or fn.endswith(".js")):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, FRONTEND_DIR)
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            for pat in call_patterns:
                for m in pat.finditer(content):
                    raw = [g for g in m.groups() if g]
                    if not raw:
                        continue
                    p = raw[0]
                    calls.append({"path": p, "file": rel, "line": content[:m.start()].count("\n") + 1})

    # Dedup by (path, file)
    seen = set()
    unique = []
    for c in calls:
        key = (c["path"], c["file"], c["line"])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


# ---------------------------------------------------------------------------
# 3. Normalization helpers
# ---------------------------------------------------------------------------
def normalize_path(p):
    """Normalize a route path for comparison. Strip {params} -> :param, trailing slashes."""
    if not p:
        return p
    p = p.strip()
    if p.startswith("${BACKEND_URL}"):
        p = p[len("${BACKEND_URL}"):]
    if p.startswith("/api/"):
        p = p[len("/api"):]
    if p.startswith("api/"):
        p = p[len("api"):]
    if p.startswith("/"):
        p = p[1:]
    # Replace {id} style placeholders
    p = re.sub(r"\{[^}]+\}", ":__id__", p)
    while p.endswith("/"):
        p = p[:-1]
    return p


def frontend_path_matches_route(front_path, route_path):
    """Check if a frontend path might match a backend route pattern."""
    fp = normalize_path(front_path)
    rp = normalize_path(route_path)
    # Template literal pieces like ${var} -> generic segment
    fp_regex = re.sub(r"\$\{[^}]+\}", ":ANY", fp)
    # replace :__id__
    rp_regex = re.sub(r":__id__", r"[^/]+", rp)
    rp_regex = re.sub(r"\{[^}]+\}", r"[^/]+", rp_regex)
    # Also allow frontend paths with template segments to match
    fp_no_var = re.sub(r":ANY", r"[^/]+", fp_regex)

    if rp == fp:
        return True
    if fp == "token":
        return False
    try:
        if re.fullmatch(rp_regex, fp):
            return True
        if re.fullmatch(fp_no_var, rp):
            return True
    except re.error:
        return False
    # Substring match for dynamic paths
    if fp.startswith(rp):
        return True
    return False


MISSING_BACKEND = []   # frontend calls with no matching backend route
MISSING_FRONTEND = []  # backend routes never referenced by frontend
STATIC_ROUTES = {"verify", "static"}  # intentional public/static

def main():
    routes = extract_backend_routes()
    calls = extract_frontend_calls()

    print("=" * 80)
    print(f"Backend routes found: {len(routes)}")
    print(f"Frontend API call sites found: {len(calls)}")
    print("=" * 80)

    # Build set of exact backend path-method combos (normalized)
    backend_keys = set()
    for r in routes:
        backend_keys.add((r["method"], normalize_path(r["path"])))

    print("\n--- Frontend API calls with NO matching backend route ---")
    for c in calls:
        fp = normalize_path(c["path"])
        if fp in {"", "token"}:
            continue
        # skip template-only paths without concrete base
        if fp.startswith(":") or fp.startswith("$"):
            continue
        matched = False
        for r in routes:
            if frontend_path_matches_route(c["path"], r["path"]):
                # method check for the common helpers
                matched = True
                break
        if not matched:
            MISSING_BACKEND.append(c)
            print(f"  MISSING: {c['path']}  (in {c['file']}:{c['line']})")

    print(f"\n  Total unmatched frontend calls: {len(MISSING_BACKEND)}")

    # Now find backend routes NOT referenced by frontend
    print("\n--- Backend routes with NO frontend reference ---")
    # collect all frontend paths
    front_paths = [c["path"] for c in calls]
    for r in routes:
        rp = normalize_path(r["path"])
        # Skip auth/static/verification/public routes that are called via direct fetch not /api
        base = rp.split("/")[0]
        if base in {"auth", "users", "static"} and r["method"] == "GET":
            pass  # /users/me and /auth/token are called from useAuth; handle below
        referenced = False
        # special-case: auth endpoints
        if rp.startswith("auth/") or rp in {"users/me"}:
            referenced = True
        if rp.startswith("ws"):
            referenced = True
        for fp in front_paths:
            if frontend_path_matches_route(fp, rp):
                referenced = True
                break
        # also check the api.js wrapper functions which use paths in the same file
        # api.js is in front_paths already since we scan it
        if not referenced:
            MISSING_FRONTEND.append(r)
            print(f"  UNREFERENCED: {r['method']} /{rp}  (in {r['file']})")

    print(f"\n  Total unreferenced backend routes: {len(MISSING_FRONTEND)}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_routes = len(routes)
    total_calls = len(calls)
    print(f"Total backend routes: {total_routes}")
    print(f"Total frontend call sites: {total_calls}")
    print(f"Frontend calls missing backend route: {len(MISSING_BACKEND)}")
    print(f"Backend routes unreferenced by frontend: {len(MISSING_FRONTEND)}")

    # Dump detail
    with open(os.path.join(ROOT, "api_connectivity_issues.json"), "w") as f:
        json.dump({
            "missing_backend": MISSING_BACKEND,
            "missing_frontend": [
                {"method": r["method"], "path": r["path"], "file": r["file"]}
                for r in MISSING_FRONTEND
            ],
        }, f, indent=2, default=str)
    print("\nDetailed dump written to api_connectivity_issues.json")


if __name__ == "__main__":
    main()

