from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select, func
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect

from .. import models, schemas, crud, auth
from ..database import engine
from ..notification_service import connection_manager, NotificationService
from ..auth import get_current_user, oauth2_scheme
from jose import jwt as jose_jwt

router = APIRouter()


async def get_user_from_token(token: str):
    """Validate token and return user."""
    from ..auth import SECRET_KEY, ALGORITHM
    try:
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = crud.get_user_by_email(email)
        return user
    except Exception:
        return None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """WebSocket endpoint for real-time notifications.
    
    Requires a valid JWT token as query parameter.
    """
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    user_id = user.id
    role = user.role or "Unknown"
    
    try:
        await connection_manager.connect(websocket, user_id, role)
        
        # Send unread count on connect
        with Session(engine) as session:
            unread_count = session.exec(
                select(func.count(models.Notification.id)).where(
                    models.Notification.user_id == user_id,
                    models.Notification.is_read == False
                )
            ).one() or 0
        
        await connection_manager.send_personal_message(user_id, {
            "type": "unread_count",
            "count": unread_count
        })
        
        while True:
            try:
                data = await websocket.receive_json()
                
                # Handle ping/pong heartbeat
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Handle typing indicators
                elif data.get("type") == "typing":
                    recipient_id = data.get("recipient_id")
                    if recipient_id:
                        await connection_manager.send_personal_message(recipient_id, {
                            "type": "message.typing",
                            "user_id": user_id,
                            "is_typing": data.get("is_typing", False)
                        })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                # Ignore malformed messages
                pass
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        import logging
        logging.error(f"WebSocket error: {e}")
    finally:
        await connection_manager.disconnect(websocket, user_id, role)


# Notification CRUD endpoints

@router.get("/notifications", response_model=dict)
def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    priority: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_archived: Optional[bool] = None,
    is_pinned: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_on",
    order: str = "desc",
    current_user=Depends(auth.get_current_user),
):
    """List notifications with filtering, search, sorting, and pagination."""
    with Session(engine) as session:
        query = select(models.Notification).where(
            models.Notification.user_id == current_user.id
        )
        
        if category:
            query = query.where(models.Notification.category == category)
        if priority:
            query = query.where(models.Notification.priority == priority)
        if is_read is not None:
            query = query.where(models.Notification.is_read == is_read)
        if is_archived is not None:
            query = query.where(models.Notification.is_archived == is_archived)
        if is_pinned is not None:
            query = query.where(models.Notification.is_pinned == is_pinned)
        if search:
            query = query.where(
                models.Notification.title.contains(search) |
                models.Notification.message.contains(search)
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()
        
        # Apply sorting
        sort_column = getattr(models.Notification, sort_by, models.Notification.created_on)
        if order.lower() == "asc":
            sort_column = sort_column.asc()
        else:
            sort_column = sort_column.desc()
        query = query.order_by(sort_column).offset(skip).limit(limit)
        
        notifications = session.exec(query).all()
        
        unread_count = session.exec(
            select(func.count(models.Notification.id)).where(
                models.Notification.user_id == current_user.id,
                models.Notification.is_read == False,
                models.Notification.is_archived == False,
            )
        ).one() or 0
        
        return {
            "notifications": notifications,
            "total": total,
            "skip": skip,
            "limit": limit,
            "unread_count": unread_count,
        }


@router.get("/notifications/unread", response_model=dict)
def get_unread_notifications(
    skip: int = 0,
    limit: int = 20,
    current_user=Depends(auth.get_current_user),
):
    """Get unread notifications with count."""
    with Session(engine) as session:
        query = select(models.Notification).where(
            models.Notification.user_id == current_user.id,
            models.Notification.is_read == False,
            models.Notification.is_archived == False,
        )
        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        notifications = session.exec(
            query.order_by(models.Notification.created_on.desc()).offset(skip).limit(limit)
        ).all()
        return {"notifications": notifications, "total": total}


@router.delete("/notifications/read", status_code=204)
async def delete_all_read_notifications(
    current_user=Depends(auth.get_current_user),
):
    """Delete all read notifications."""
    with Session(engine) as session:
        notifications = session.exec(
            select(models.Notification).where(
                models.Notification.user_id == current_user.id,
                models.Notification.is_read == True,
            )
        ).all()
        for n in notifications:
            session.delete(n)
        session.commit()


@router.get("/notifications/preferences", response_model=schemas.NotificationPreferenceRead)
def get_notification_preferences(
    current_user=Depends(auth.get_current_user),
):
    """Get notification preferences for current user."""
    with Session(engine) as session:
        prefs = session.exec(
            select(models.NotificationPreference).where(
                models.NotificationPreference.user_id == current_user.id
            )
        ).first()
        
        if not prefs:
            # Create default preferences
            prefs = models.NotificationPreference(user_id=current_user.id)
            session.add(prefs)
            session.commit()
            session.refresh(prefs)
        
        return prefs


@router.put("/notifications/preferences", response_model=schemas.NotificationPreferenceRead)
def update_notification_preferences(
    prefs_update: schemas.NotificationPreferenceCreate,
    current_user=Depends(auth.get_current_user),
):
    """Update notification preferences."""
    with Session(engine) as session:
        prefs = session.exec(
            select(models.NotificationPreference).where(
                models.NotificationPreference.user_id == current_user.id
            )
        ).first()
        
        if not prefs:
            prefs = models.NotificationPreference(user_id=current_user.id)
        
        update_data = prefs_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(prefs, k, v)
        
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
        return prefs


@router.get("/notifications/{notification_id}", response_model=schemas.NotificationRead)
def get_notification(
    notification_id: int,
    current_user=Depends(auth.get_current_user),
):
    """Get a single notification."""
    with Session(engine) as session:
        notification = session.get(models.Notification, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this notification")
        return notification


@router.post("/notifications", response_model=schemas.NotificationRead, status_code=201)
async def create_notification(
    notification_in: schemas.NotificationCreate,
    current_user=Depends(auth.require_roles("Super Admin", "School Admin", "Principal")),
):
    """Create a notification (admin only)."""
    notification = await NotificationService.create_and_send(
        user_id=notification_in.user_id,
        title=notification_in.title,
        message=notification_in.message,
        category=notification_in.category,
        priority=notification_in.priority,
        related_module=notification_in.related_module,
        related_record_id=notification_in.related_record_id,
        sender_id=notification_in.sender_id or current_user.id,
    )
    return notification


@router.put("/notifications/{notification_id}/read", response_model=schemas.NotificationRead)
async def mark_notification_read(
    notification_id: int,
    current_user=Depends(auth.get_current_user),
):
    """Mark a single notification as read."""
    with Session(engine) as session:
        notification = session.get(models.Notification, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        notification.is_read = True
        session.add(notification)
        session.commit()
        session.refresh(notification)
    
    # Notify via WebSocket
    await connection_manager.send_personal_message(current_user.id, {
        "type": "notification.read",
        "notification_id": notification_id,
    })
    
    return notification


@router.delete("/notifications/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: int,
    current_user=Depends(auth.get_current_user),
):
    """Delete a notification."""
    with Session(engine) as session:
        notification = session.get(models.Notification, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        session.delete(notification)
        session.commit()
    
    # Notify via WebSocket
    await connection_manager.send_personal_message(current_user.id, {
        "type": "notification.deleted",
        "notification_id": notification_id,
    })


@router.put("/notifications/{notification_id}/archive", response_model=schemas.NotificationRead)
async def archive_notification(
    notification_id: int,
    current_user=Depends(auth.get_current_user),
):
    """Archive a notification."""
    with Session(engine) as session:
        notification = session.get(models.Notification, notification_id)
        if not notification:
            raise HTTPException(status_code=404)
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403)
        notification.is_archived = True
        session.add(notification)
        session.commit()
        session.refresh(notification)
    return notification


@router.put("/notifications/{notification_id}/restore", response_model=schemas.NotificationRead)
async def restore_archived_notification(
    notification_id: int,
    current_user=Depends(auth.get_current_user),
):
    """Restore an archived notification."""
    with Session(engine) as session:
        notification = session.get(models.Notification, notification_id)
        if not notification:
            raise HTTPException(status_code=404)
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403)
        notification.is_archived = False
        session.add(notification)
        session.commit()
        session.refresh(notification)
    return notification


@router.put("/notifications/{notification_id}/pin", response_model=schemas.NotificationRead)
async def pin_notification(
    notification_id: int,
    current_user=Depends(auth.get_current_user),
):
    """Pin/unpin a notification."""
    with Session(engine) as session:
        notification = session.get(models.Notification, notification_id)
        if not notification:
            raise HTTPException(status_code=404)
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403)
        notification.is_pinned = not notification.is_pinned
        session.add(notification)
        session.commit()
        session.refresh(notification)
    return notification

