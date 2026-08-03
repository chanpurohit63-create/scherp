from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
import os
from sqlmodel import SQLModel, Session, select, func
from datetime import datetime
from . import models, schemas, auth, crud
from .tenant import get_current_school_id as _get_sid, set_current_school_id as _set_sid
from .database import engine, init_db
from .routers import users as users_router, erp as erp_router, notifications as notifications_router, superadmin as superadmin_router, timetable as timetable_router, report_cards as report_cards_router, report_card as enterprise_report_card_router
from .notification_service import connection_manager

app = FastAPI(title="School ERP - Backend (FastAPI)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@app.on_event("startup")
def on_startup():
    init_db()
    os.makedirs("static/uploads", exist_ok=True)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/auth/register", response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate, school_id: int = Query(..., description="School ID to register under")):
    """Register a new user under a specific school.
    school_id is required and must reference an active school.
    Super Admin users cannot be created via registration."""
    existing = crud.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Validate school exists and is active
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    if school.status != "active":
        raise HTTPException(status_code=403, detail=f"Cannot register: school is {school.status}")
    # Prevent creating Super Admin via registration
    if user_in.role == "Super Admin":
        raise HTTPException(status_code=403, detail="Cannot register as Super Admin")
    hashed = auth.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed, full_name=user_in.full_name, role=user_in.role, school_id=school_id)
    created = crud.create_user(user)
    return schemas.UserRead(id=created.id, email=created.email, full_name=created.full_name, role=created.role, is_active=created.is_active, school_id=created.school_id)


@app.post("/auth/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    # Include school_id and user_id in JWT for tenant isolation
    access_token = auth.create_access_token({
        "sub": user.email,
        "role": user.role,
        "school_id": user.school_id,
        "user_id": user.id,
    })
    return {"access_token": access_token, "token_type": "bearer", "school_id": user.school_id}


@app.get("/users/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(auth.get_current_user)):
    return schemas.UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        school_id=current_user.school_id,
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """WebSocket endpoint for real-time notifications."""
    from jose import jwt as jose_jwt
    try:
        payload = jose_jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user = crud.get_user_by_email(email)
    if not user:
        await websocket.close(code=4001, reason="User not found")
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

                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
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
            except Exception:
                pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        import logging
        logging.error(f"WebSocket error: {e}")
    finally:
        await connection_manager.disconnect(websocket, user_id, role)


app.include_router(users_router.router, prefix="/api")
app.include_router(erp_router.router, prefix="/api")
app.include_router(notifications_router.router, prefix="/api")
app.include_router(superadmin_router.router, prefix="/api/superadmin")
app.include_router(timetable_router.router, prefix="/api")
app.include_router(report_cards_router.router, prefix="/api")
app.include_router(enterprise_report_card_router.router, prefix="/api")
