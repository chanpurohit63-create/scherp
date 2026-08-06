"""Find exact line numbers for routes to fix"""
with open('backend/app/routers/erp.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find parent routes
print("=== PARENT ROUTES ===")
for i, line in enumerate(lines, 1):
    if '@router.' in line and '/parents' in line:
        print(f"  Line {i}: {line.strip()}")

# Find notice routes
print("\n=== NOTICE ROUTES ===")
for i, line in enumerate(lines, 1):
    if '@router.' in line and '/notices' in line:
        print(f"  Line {i}: {line.strip()}")

# Find the filter_notices function
print("\n=== FILTER NOTICES ===")
for i, line in enumerate(lines, 1):
    if 'def filter_notices' in line:
        print(f"  Line {i}: {line.strip()}")
        # Print surrounding lines
        for j in range(max(0, i-3), min(len(lines), i+10)):
            print(f"    {j+1}: {lines[j].rstrip()}")