"""Fix timetable_service - use current_user.school_id instead of _get_school_id()."""
import re

# Fix create_period_master
path = "backend/app/timetable_service.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the _get_school_id() calls in create_period_master and similar
old = """def create_period_master(period_in: schemas.PeriodMasterCreate, current_user: models.User) -> models.PeriodMaster:
    sid = _get_school_id()"""
new = """def create_period_master(period_in: schemas.PeriodMasterCreate, current_user: models.User) -> models.PeriodMaster:
    sid = current_user.school_id"""
assert old in content, "create_period_master not found"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Timetable service fixed")