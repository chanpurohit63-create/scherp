"""Tenant context module for multi-tenant isolation.

Uses contextvars to store the current school_id per-request.
This allows all database queries to automatically filter by school_id
without passing it through every function call.
"""
from contextvars import ContextVar
from typing import Optional

# Context variable to hold the current school_id for the active request
_current_school_id: ContextVar[Optional[int]] = ContextVar("_current_school_id", default=None)


def set_current_school_id(school_id: Optional[int]) -> None:
    """Set the current school_id in the context."""
    _current_school_id.set(school_id)


def get_current_school_id() -> Optional[int]:
    """Get the current school_id from the context.
    Returns None for Super Admin (platform-wide access)."""
    return _current_school_id.get()


def clear_current_school_id() -> None:
    """Clear the current school_id from the context."""
    _current_school_id.set(None)