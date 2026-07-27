from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
import os
from sqlmodel import SQLModel
from . import models, schemas, auth, crud
from .database import engine, init_db
from .routers import users as users_router, erp as erp_router

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
    if not app.router.routes:
        pass

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/auth/register", response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate):
    existing = crud.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed, full_name=user_in.full_name, role=user_in.role)
    created = crud.create_user(user)
    return schemas.UserRead(id=created.id, email=created.email, full_name=created.full_name, role=created.role, is_active=created.is_active)


@app.post("/auth/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token = auth.create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead)
def read_me(token: str = Depends(oauth2_scheme)):
    from jose import jwt
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_email(email)
    return schemas.UserRead(id=user.id, email=user.email, full_name=user.full_name, role=user.role, is_active=user.is_active)


app.include_router(users_router.router, prefix="/api")
app.include_router(erp_router.router, prefix="/api")
