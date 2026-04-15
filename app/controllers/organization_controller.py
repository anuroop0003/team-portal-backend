from uuid import UUID
from sqlalchemy.orm import Session
from app.services import organization_service

def create_organization(db: Session, org_data):
    return organization_service.create_organization(db, org_data)

def get_organizations(db: Session):
    return organization_service.get_organizations(db)

def get_organization_by_id(db: Session, org_id: UUID):
    return organization_service.get_organization_by_id(db, org_id)

def suspend_organization(db: Session, org_id: UUID):
    return organization_service.suspend_organization(db, org_id)

def unsuspend_organization(db: Session, org_id: UUID):
    return organization_service.unsuspend_organization(db, org_id)

def delete_organization(db: Session, org_id: UUID):
    return organization_service.delete_organization(db, org_id)
