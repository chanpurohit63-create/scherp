"""Audit logging module for centralized audit trail."""
from typing import Optional
from datetime import datetime
from sqlmodel import Session
from . import models
from .database import engine


def log_audit(
    user_id: Optional[int] = None,
    school_id: Optional[int] = None,
    action: str = "",
    resource: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
    before_values: Optional[str] = None,
    after_values: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Create an audit log entry."""
    audit = models.AuditLog(
        user_id=user_id,
        school_id=school_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        before_values=before_values,
        after_values=after_values,
        ip_address=ip_address,
    )
    with Session(engine) as session:
        session.add(audit)
        session.commit()


def get_client_ip(request) -> Optional[str]:
    """Extract client IP from request."""
    if request.client:
        return request.client.host
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return None