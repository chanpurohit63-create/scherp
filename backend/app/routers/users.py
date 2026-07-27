from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlmodel import Session, select

from .. import schemas, models, crud, auth
from ..database import engine

router = APIRouter()


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    existing = crud.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed, full_name=user_in.full_name, role=user_in.role)
    created = crud.create_user(user)
    return schemas.UserRead(id=created.id, email=created.email, full_name=created.full_name, role=created.role, is_active=created.is_active)


@router.get("/users", response_model=List[schemas.UserRead])
def list_users(skip: int = 0, limit: int = 100, current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    users = crud.get_users(skip=skip, limit=limit)
    return [schemas.UserRead(id=u.id, email=u.email, full_name=u.full_name, role=u.role, is_active=u.is_active) for u in users]


@router.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    user = crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserRead(id=user.id, email=user.email, full_name=user.full_name, role=user.role, is_active=user.is_active)


@router.put("/users/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    values = user_update.dict(exclude_unset=True)
    user = crud.update_user(user_id, values)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserRead(id=user.id, email=user.email, full_name=user.full_name, role=user.role, is_active=user.is_active)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    ok = crud.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {}


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    # Placeholder: implement email token flow in production
    user = crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # In real app, generate token and send email. Return success for scaffold.
    return {"msg": "Password reset requested (placeholder)"}


@router.post("/roles", response_model=schemas.RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role_in: schemas.RoleCreate, current_user: models.User = Depends(auth.require_roles("Super Admin"))):
    role = models.Role(name=role_in.name, description=role_in.description)
    with Session(engine) as session:
        session.add(role)
        session.commit()
        session.refresh(role)
    return schemas.RoleRead(id=role.id, name=role.name, description=role.description)


@router.get("/roles", response_model=List[schemas.RoleRead])
def list_roles(current_user: models.User = Depends(auth.require_roles("Super Admin", "School Admin"))):
    with Session(engine) as session:
        statement = select(models.Role)
        roles = session.exec(statement).all()
        return [schemas.RoleRead(id=r.id, name=r.name, description=r.description) for r in roles]
