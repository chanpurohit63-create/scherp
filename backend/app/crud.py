from typing import Optional, Type, TypeVar, List
from sqlmodel import Session, select, SQLModel, func
from sqlalchemy import or_
from .models import User, School
from .database import engine
from .tenant import get_current_school_id

ModelType = TypeVar("ModelType", bound=SQLModel)


def _tenant_school_id(school_id: Optional[int]) -> Optional[int]:
    """Use provided school_id, or fall back to tenant context.
    Returns None for Super Admin (no filtering)."""
    if school_id is not None:
        return school_id
    return get_current_school_id()


# ========== USER CRUD ==========

def get_user_by_email(email: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()


def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_users(skip: int = 0, limit: int = 100, school_id: Optional[int] = None):
    sid = _tenant_school_id(school_id)
    with Session(engine) as session:
        statement = select(User)
        if sid is not None:
            statement = statement.where(User.school_id == sid)
        statement = statement.offset(skip).limit(limit)
        return session.exec(statement).all()


def get_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        # Tenant isolation: verify user belongs to current tenant
        sid = get_current_school_id()
        if sid is not None and user.school_id != sid:
            return None  # Not found in this tenant
        return user


def update_user(user_id: int, values: dict):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        # Tenant isolation: verify user belongs to current tenant
        sid = get_current_school_id()
        if sid is not None and user.school_id != sid:
            return None  # Not found in this tenant
        # Prevent school_id override from client input
        if "school_id" in values and values["school_id"] != user.school_id:
            if sid is not None:  # Only super admin can change school_id
                del values["school_id"]
        for k, v in values.items():
            setattr(user, k, v)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return False
        # Tenant isolation: verify user belongs to current tenant
        sid = get_current_school_id()
        if sid is not None and user.school_id != sid:
            return False  # Not found in this tenant
        session.delete(user)
        session.commit()
        return True


# ========== SCHOOL CRUD (Super Admin) ==========

def create_school(school: School):
    with Session(engine) as session:
        session.add(school)
        session.commit()
        session.refresh(school)
        return school


def get_school(school_id: int):
    with Session(engine) as session:
        return session.get(School, school_id)


def get_school_by_code(school_code: str):
    with Session(engine) as session:
        statement = select(School).where(School.school_code == school_code)
        return session.exec(statement).first()


def list_schools(skip: int = 0, limit: int = 100, status: Optional[str] = None, search: Optional[str] = None):
    with Session(engine) as session:
        statement = select(School)
        if status:
            statement = statement.where(School.status == status)
        if search:
            statement = statement.where(
                or_(
                    School.school_name.contains(search),
                    School.school_code.contains(search),
                    School.email.contains(search),
                    School.city.contains(search),
                )
            )
        statement = statement.offset(skip).limit(limit)
        return session.exec(statement).all()


def count_schools(status: Optional[str] = None) -> int:
    with Session(engine) as session:
        statement = select(func.count(School.id))
        if status:
            statement = statement.where(School.status == status)
        return session.exec(statement).one()


def update_school(school_id: int, values: dict):
    with Session(engine) as session:
        school = session.get(School, school_id)
        if not school:
            return None
        for k, v in values.items():
            setattr(school, k, v)
        session.add(school)
        session.commit()
        session.refresh(school)
        return school


def delete_school(school_id: int):
    with Session(engine) as session:
        school = session.get(School, school_id)
        if not school:
            return False
        session.delete(school)
        session.commit()
        return True


# ========== GENERIC ITEM CRUD (Tenant-Scoped) ==========

def create_item(item: SQLModel):
    """Create item. Automatically sets school_id from tenant context if not already set."""
    sid = get_current_school_id()
    if sid is not None and hasattr(item, "school_id") and not getattr(item, "school_id", None):
        item.school_id = sid
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


def get_item(model: Type[ModelType], item_id: int, school_id: Optional[int] = None) -> Optional[ModelType]:
    """Get item by ID. Automatically verifies tenant ownership."""
    sid = _tenant_school_id(school_id)
    with Session(engine) as session:
        item = session.get(model, item_id)
        if not item:
            return None
        # Tenant isolation: if sid is set and item has school_id, verify match
        if sid is not None and hasattr(item, "school_id"):
            if item.school_id != sid:
                return None  # Not found in this tenant (prevents IDOR)
        return item


def list_items(model: Type[ModelType], skip: int = 0, limit: int = 100, school_id: Optional[int] = None):
    """List items. Automatically filters by tenant school_id."""
    sid = _tenant_school_id(school_id)
    with Session(engine) as session:
        statement = select(model)
        if sid is not None and hasattr(model, "school_id"):
            statement = statement.where(model.school_id == sid)
        statement = statement.offset(skip).limit(limit)
        return session.exec(statement).all()


def update_item(model: Type[ModelType], item_id: int, values: dict, school_id: Optional[int] = None) -> Optional[ModelType]:
    """Update item. Automatically verifies tenant ownership."""
    sid = _tenant_school_id(school_id)
    with Session(engine) as session:
        item = session.get(model, item_id)
        if not item:
            return None
        # Tenant isolation check
        if sid is not None and hasattr(item, "school_id"):
            if item.school_id != sid:
                return None  # Not found in this tenant
        for k, v in values.items():
            setattr(item, k, v)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


def delete_item(model: Type[ModelType], item_id: int, school_id: Optional[int] = None) -> bool:
    """Delete item. Automatically verifies tenant ownership."""
    sid = _tenant_school_id(school_id)
    with Session(engine) as session:
        item = session.get(model, item_id)
        if not item:
            return False
        # Tenant isolation check
        if sid is not None and hasattr(item, "school_id"):
            if item.school_id != sid:
                return False  # Not found in this tenant
        session.delete(item)
        session.commit()
        return True


def count_items(model: Type[ModelType], school_id: Optional[int] = None) -> int:
    """Count items, automatically filtered by tenant school_id."""
    sid = _tenant_school_id(school_id)
    with Session(engine) as session:
        statement = select(func.count(model.id))
        if sid is not None and hasattr(model, "school_id"):
            statement = statement.where(model.school_id == sid)
        return session.exec(statement).one()