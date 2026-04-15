from uuid import UUID
from sqlalchemy.orm import Session
from app.services import user_service

def create_user(db: Session, user_data):
    return user_service.create_user(db, user_data)

def get_users(db: Session, organization_id: UUID, skip: int = 0, limit: int = 100, search: str = None):
    return user_service.get_users(db, organization_id, skip, limit, search)

def get_user_by_id(db: Session, user_id: UUID, organization_id: UUID):
    return user_service.get_user_by_id(db, user_id, organization_id)

def update_user(db: Session, user_id: UUID, organization_id: UUID, update_data):
    return user_service.update_user(db, user_id, organization_id, update_data)

def delete_user(db: Session, user_id: UUID, organization_id: UUID):
    return user_service.delete_user(db, user_id, organization_id)

def deactivate_user(db: Session, user_id: UUID, organization_id: UUID):
    return user_service.deactivate_user(db, user_id, organization_id)