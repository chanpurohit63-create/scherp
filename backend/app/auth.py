from datetime import datetime, timedelta
from typing import Optional
import os

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from . import crud
from .models import User, School
from .database import engine
from .tenant import set_current_school_id, clear_current_school_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# School statuses that are allowed to access protected modules
ACTIVE_SCHOOL_STATUSES = {"active"}  # Only active schools can login
BLOCKED_SCHOOL_STATUSES = {"suspended", "inactive", "deleted", "expired"}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Ensure school_id and user_id are in the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        school_id = payload.get("school_id")
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = crud.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    # Validate token's school_id matches user's school_id (prevents school_id tampering)
    token_school_id = school_id or user.school_id
    if token_school_id != user.school_id and user.role != "Super Admin":
        # Token was crafted with wrong school_id - security issue
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    # Use school_id from token (never trust frontend), fallback to user's school_id
    user.school_id = token_school_id
    # Check if user's school is blocked
    if user.role != "Super Admin":
        school_status = get_school_status(user.school_id)
        if school_status in BLOCKED_SCHOOL_STATUSES:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"School access blocked (status: {school_status})")
    # Set tenant context for automatic school_id filtering in queries
    # Super Admin has school_id but should see all data (None = no filter)
    if user.role == "Super Admin":
        set_current_school_id(None)
    else:
        set_current_school_id(user.school_id)
    return user


def get_school_status(school_id: Optional[int]) -> str:
    """Get the status of the school. Returns 'active' for super admin (no school)."""
    if not school_id:
        return "active"  # Super Admin has no school
    with Session(engine) as session:
        school = session.get(School, school_id)
        if not school:
            return "deleted"
        # Auto-expire if subscription_end is in the past
        if school.status == "active" and school.subscription_end:
            from datetime import date
            if school.subscription_end < date.today():
                school.status = "expired"
                session.add(school)
                session.commit()
                return "expired"
        return school.status


def require_roles(*allowed_roles: str):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != "Super Admin" and current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return current_user
    return role_checker


def require_super_admin(current_user=Depends(get_current_user)):
    """Only Super Admin can access these endpoints."""
    if current_user.role != "Super Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin access required")
    return current_user


def require_school_access(current_user=Depends(get_current_user)):
    """Super Admin can access any school. Other users are scoped to their own school.
    Also validates that the school is not suspended/inactive/deleted."""
    if current_user.role == "Super Admin":
        return current_user
    if not current_user.school_id:
        raise HTTPException(status_code=403, detail="No school access")
    # Check school status
    school_status = get_school_status(current_user.school_id)
    if school_status in BLOCKED_SCHOOL_STATUSES:
        raise HTTPException(status_code=403, detail=f"School access blocked (status: {school_status})")
    return current_user


def require_active_school(current_user=Depends(get_current_user)):
    """For write operations - school must be active (not expired/suspended).
    Super Admin bypasses this check."""
    if current_user.role == "Super Admin":
        return current_user
    if not current_user.school_id:
        raise HTTPException(status_code=403, detail="No school access")
    school_status = get_school_status(current_user.school_id)
    if school_status != "active":
        raise HTTPException(status_code=403, detail=f"School is not active (status: {school_status}). Editing restricted.")
    return current_user


def get_school_id(current_user=Depends(require_school_access)) -> int:
    """Get the current school_id from the authenticated user.
    Never trust school_id from the frontend - always derive from JWT."""
    return current_user.school_id


def get_school_id_optional(current_user=Depends(get_current_user)) -> Optional[int]:
    """Get school_id, returns None for Super Admin."""
    if current_user.role == "Super Admin":
        return None
    return current_user.school_id