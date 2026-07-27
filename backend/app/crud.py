from typing import Optional, Type, TypeVar
from sqlmodel import Session, select, SQLModel
from .models import User
from .database import engine

ModelType = TypeVar("ModelType", bound=SQLModel)


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


def get_users(skip: int = 0, limit: int = 100):
    with Session(engine) as session:
        statement = select(User).offset(skip).limit(limit)
        return session.exec(statement).all()


def get_user(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)


def update_user(user_id: int, values: dict):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
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
        session.delete(user)
        session.commit()
        return True


def create_item(item: SQLModel):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


def get_item(model: Type[ModelType], item_id: int) -> Optional[ModelType]:
    with Session(engine) as session:
        return session.get(model, item_id)


def list_items(model: Type[ModelType], skip: int = 0, limit: int = 100):
    with Session(engine) as session:
        statement = select(model).offset(skip).limit(limit)
        return session.exec(statement).all()


def update_item(model: Type[ModelType], item_id: int, values: dict) -> Optional[ModelType]:
    with Session(engine) as session:
        item = session.get(model, item_id)
        if not item:
            return None
        for k, v in values.items():
            setattr(item, k, v)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


def delete_item(model: Type[ModelType], item_id: int) -> bool:
    with Session(engine) as session:
        item = session.get(model, item_id)
        if not item:
            return False
        session.delete(item)
        session.commit()
        return True
