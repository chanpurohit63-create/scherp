"""Fix remaining bugs: homework submission school_id and report_cards PDF."""
import re

# 1. Fix student_submit_homework to set school_id
path = "backend/app/routers/erp.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the HomeworkSubmission creation in student_submit_homework
old = """            sub = models.HomeworkSubmission(
                homework_id=homework_id, student_id=student.id,
                attachment_path=attachment_path, remarks=remarks, status="submitted"
            )"""
new = """            sub = models.HomeworkSubmission(
                homework_id=homework_id, student_id=student.id,
                attachment_path=attachment_path, remarks=remarks, status="submitted",
                school_id=current_user.school_id,
            )"""
assert old in content, "HomeworkSubmission creation not found"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# 2. Fix report_cards.py PDF generation
path2 = "backend/app/routers/report_cards.py"
with open(path2, "r", encoding="utf-8") as f:
    content2 = f.read()

# Replace all .encode('latin-1') patterns
content2 = content2.replace(
    "pdf.output(dest='S').encode('latin-1')",
    "bytes(pdf.output(dest='S'))"
)

with open(path2, "w", encoding="utf-8") as f:
    f.write(content2)

print("Remaining fixes applied")