"""Apply school_id fixes to erp.py - pass current_user to create_resource."""
import re

path = "backend/app/routers/erp.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update create_resource helper to accept current_user (handle both old and new)
old_helper1 = """def create_resource(resource_in, model):
    resource = model(**resource_in.dict())
    return crud.create_item(resource)"""
new_helper = """def create_resource(resource_in, model, current_user=None):
    resource = model(**resource_in.dict())
    # Explicitly set school_id from current_user to avoid contextvar propagation issues
    if current_user and hasattr(resource, "school_id") and not getattr(resource, "school_id", None):
        resource.school_id = current_user.school_id
    return crud.create_item(resource)"""
if old_helper1 in content:
    content = content.replace(old_helper1, new_helper)
else:
    # Check if already updated
    assert "current_user=None" in content, "Helper not found in either state"
    print("Helper already updated")

# 2. Update all create_resource calls to pass current_user
# Pattern: create_resource(X, models.Y) -> create_resource(X, models.Y, current_user)
# But NOT the ones that already have current_user
content = re.sub(
    r'create_resource\(([^,]+), (models\.[A-Za-z_]+)\)',
    r'create_resource(\1, \2, current_user)',
    content
)

# 3. Fix create_room to use current_user.school_id instead of get_current_school_id()
old_room = """def create_room(room_in: schemas.RoomCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    with Session(engine) as session:
        sid = get_current_school_id()
        if sid is not None:"""
new_room = """def create_room(room_in: schemas.RoomCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    with Session(engine) as session:
        sid = current_user.school_id
        if sid is not None:"""
assert old_room in content, "Room not found"
content = content.replace(old_room, new_room)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixes applied successfully")