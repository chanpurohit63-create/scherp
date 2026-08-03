"""Fix the register function in e2e_master_test.py"""
import os

filepath = "e2e_master_test.py"
if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
    print("File is empty or doesn't exist. Cannot fix.")
    exit(1)

content = open(filepath, "r", encoding="utf-8").read()

# Fix the register function - change the "exist" check to also check for "already" and status 400
old_check = 'if "exist" in r.text.lower():'
new_check = 'if r.status_code == 400 or "already" in r.text.lower() or "exist" in r.text.lower():'

if old_check in content:
    content = content.replace(old_check, new_check)
    print("Fixed register function check")
else:
    print("Register function check not found (might already be fixed or different format)")

# Also fix the comment
old_comment = '# User exists, find user_id via login'
new_comment = '# User might exist, try login to get user_id'
if old_comment in content:
    content = content.replace(old_comment, new_comment)

open(filepath, "w", encoding="utf-8").write(content)
print("File saved successfully")
print(f"File size: {os.path.getsize(filepath)} bytes")