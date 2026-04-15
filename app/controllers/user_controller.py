from sqlalchemy.orm import Session
from app.services import user_service

def create_user(db: Session, user_data):
    return user_service.create_user(db, user_data)

def get_users(db: Session):
    return user_service.get_users(db)


def get_user_by_id(db: Session, user_id: int):
    return user_service.get_user_by_id(db, user_id)


def deactivate_user(db: Session, user_id: int):
    return user_service.deactivate_user(db, user_id)