"""Check whether specific frontend-expected backend routes exist."""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

# Frontend api.js wrapper paths that need backend routes
frontend_paths = [
    "report-card/templates",
    "report-card/components",
    "report-card/components/template/{}",
    "examination-types",
    "exam-weightage",
    "grade-scales",
    "grade-scale-ranges",
    "gpa-engines",
    "gpa-mappings",
    "subject-categories",
    "subject-category-mappings",
]

router_files = [
    "backend/app/routers/users.py",
    "backend/app/routers/erp.py",
    "backend/app/routers/notifications.py",
    "backend/app/routers/superadmin.py",
    "backend/app/routers/timetable.py",
    "backend/app/routers/report_cards.py",
    "backend/app/main.py",
]

# Collect all backend route paths
all_routes = []
for rf in router_files:
    path = os.path.join(ROOT, rf)
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    pattern = re.compile(r"@(?:router|app)\.(get|post|put|delete|websocket)\("
                         r"(?P<path>['\"][^'\"]+['\"])")
    for m in pattern.finditer(content):
        all_routes.append(m.group(2).strip("'\""))

print("=== Search for backend routes matching frontend wrapper paths ===\n")
for fp in frontend_paths:
    base = fp.split("/")[0]
    found = [r for r in all_routes if base in r]
    # check if any route matches the full path pattern
    exact = [r for r in all_routes if fp in r or fp.split("/")[0] in r]
    print(f"FRONTEND expects: {fp}")
    print(f"  Matching backend routes: {exact if exact else 'NONE FOUND'}")
    print()

# Also check what router files define these - search across all backend py files
print("=== Search entire backend for these route keywords ===")
keywords = ["report-card/templates", "report-card/components", "examination-types",
            "exam-weightage", "grade-scales", "gpa-engines", "subject-categories",
            "subject-category-mappings", "grade-scale-ranges", "gpa-mappings"]
for kw in keywords:
    found_in = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "backend")):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue
            if kw in content:
                found_in.append(full)
    print(f"{kw}: {found_in if found_in else 'NOT FOUND anywhere in backend'}")
