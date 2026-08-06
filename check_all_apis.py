"""Comprehensive frontend-backend API matching checker."""
import re
import json
import os

ROOT = "."
FRONTEND_SRC = os.path.join(ROOT, "frontend", "src")
BACKEND = os.path.join(ROOT, "backend", "app")

# ========== 1. Extract all backend routes ==========
backend_routes = []  # (method, path)

for fname in os.listdir(os.path.join(BACKEND, "routers")):
    if not fname.endswith(".py"):
        continue
    fpath = os.path.join(BACKEND, "routers", fname)
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # Find router decorators
    for m in re.finditer(r'@router\.(get|post|put|delete|patch)\("([^"]+)"', content):
        method = m.group(1).upper()
        path = m.group(2)
        backend_routes.append((method, path))

# Add main.py routes
with open(os.path.join(BACKEND, "main.py"), "r", encoding="utf-8") as f:
    content = f.read()
for m in re.finditer(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', content):
    method = m.group(1).upper()
    path = m.group(2)
    backend_routes.append((method, path))

print(f"Total backend routes found: {len(backend_routes)}")

# ========== 2. Extract all frontend API calls ==========
frontend_calls = []  # (path_string, file, line)

for root, dirs, files in os.walk(FRONTEND_SRC):
    for fname in files:
        if not fname.endswith((".js", ".jsx")):
            continue
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, ROOT)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            # Look for fetch calls, listResources, createResource, etc.
            for m in re.finditer(r'(?:fetch|listResources|createResource|postResource|getResource|updateResource|deleteResource|uploadFile|downloadFile|fetchText)\([^,]*,\s*["\'`]([^"\'`]+)["\'`]', line):
                path_str = m.group(1)
                frontend_calls.append((path_str, rel, i))
            # Look for template literals with API paths
            for m in re.finditer(r'(?:listResources|createResource|postResource|getResource|updateResource|deleteResource|uploadFile|downloadFile)\s*\(\s*[^,]+,\s*`([^`]+)`', line):
                path_str = m.group(1)
                frontend_calls.append((path_str, rel, i))
            # Look for BACKEND_URL direct fetches
            for m in re.finditer(r'BACKEND_URL\s*\+\s*["\'`]/(api/[^"\'`${]+|auth/[^"\'`${]+|users/[^"\'`${]+|static/[^"\'`${]+)', line):
                path_str = m.group(1)
                frontend_calls.append(("DIRECT:" + path_str, rel, i))

print(f"Total frontend API calls found: {len(frontend_calls)}")

# ========== 3. Match ==========
def normalize_route_path(path):
    """Convert a route path with {param} to a regex-comparable pattern."""
    # Remove query strings
    path = path.split("?")[0]
    # Replace {param} with a catch-all
    path = re.sub(r"\{[^}]+\}", "*", path)
    return path

def match_path(front_path, backend_path):
    """Check if frontend path matches backend path pattern."""
    fp = front_path.split("?")[0].strip()
    bp = backend_path.strip()
    
    # Normalize: remove leading /api/ from frontend if present
    if fp.startswith("/api/"):
        fp = fp[5:]
    elif fp.startswith("api/"):
        fp = fp[4:]
    
    # Convert both to segments
    f_segs = [s for s in fp.split("/") if s]
    b_segs = [s for s in bp.split("/") if s]
    
    if len(f_segs) != len(b_segs):
        return False
    
    for f, b in zip(f_segs, b_segs):
        if b.startswith("{") and b.endswith("}"):
            continue  # parameter match
        if f != b:
            return False
    return True

backend_paths = [p for _, p in backend_routes]

unmatched = []
for path_str, file, line in frontend_calls:
    if path_str.startswith("DIRECT:"):
        continue
    # Skip static file references
    if path_str.startswith("static/"):
        continue
    # Skip empty paths
    if not path_str:
        continue
    # Skip paths that start with variables
    if path_str.startswith("${") or path_str.startswith("$"):
        continue
    
    # Try exact match or pattern match
    matched = False
    for bpath in backend_paths:
        if normalize_route_path(path_str) == normalize_route_path(bpath) or match_path(path_str, bpath):
            matched = True
            break
    
    if not matched:
        unmapped = path_str.replace("${", "$").replace("}", "")
        unmatched.append({"path": path_str, "file": file, "line": line})

print(f"\n=== UNMATCHED FRONTEND API CALLS ({len(unmatched)}) ===")
for u in unmatched:
    print(f"  {u['path']}  ({u['file']}:{u['line']})")

# ========== 4. Check backend routes not used by frontend ==========
used_paths = set()
for path_str, file, line in frontend_calls:
    if path_str.startswith("DIRECT:"):
        used_paths.add(path_str[7:])
        continue
    for bpath in backend_paths:
        if match_path(path_str, bpath) or normalize_route_path(path_str) == normalize_route_path(bpath):
            used_paths.add(bpath)

unused = []
for method, path in backend_routes:
    if path not in used_paths:
        unused.append({"method": method, "path": path})

print(f"\n=== BACKEND ROUTES NOT DIRECTLY MATCHED BY FRONTEND ({len(unused)}) ===")
for u in unused[:80]:
    print(f"  {u['method']} {u['path']}")
if len(unused) > 80:
    print(f"  ... and {len(unused) - 80} more")

# Save results
with open("api_match_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "backend_routes_total": len(backend_routes),
        "frontend_calls_total": len(frontend_calls),
        "unmatched_frontend": unmatched,
        "unused_backend_routes": unused,
    }, f, indent=2, default=str)

print("\nResults saved to api_match_results.json")