from uuid import UUID
from sqlalchemy.orm import Session
from app.models.organization_model import Organization

def create_organization(db: Session, org_data):
    existing = db.query(Organization).filter(Organization.initial == org_data.initial).first()
    if existing:
        raise Exception("Organization with this initial already exists")
    
    new_org = Organization(
        name=org_data.name,
        full_name=org_data.full_name,
        initial=org_data.initial.upper(),
        logo_url=org_data.logo_url
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

def get_organizations(db: Session):
    return db.query(Organization).all()

def get_organization_by_id(db: Session, org_id: UUID):
    return db.query(Organization).filter(Organization.id == org_id).first()

def suspend_organization(db: Session, org_id: UUID):
    org = get_organization_by_id(db, org_id)
    if not org:
        raise Exception("Organization not found")
    
    org.is_active = False
    
    # Bulk update all users in this organization
    from app.models.user_model import User
    db.query(User).filter(User.organization_id == org_id).update({"is_active": False})
    
    db.commit()
    return org

def unsuspend_organization(db: Session, org_id: UUID):
    org = get_organization_by_id(db, org_id)
    if not org:
        raise Exception("Organization not found")
    
    org.is_active = True
    
    # Bulk restore all users in this organization
    from app.models.user_model import User
    db.query(User).filter(User.organization_id == org_id).update({"is_active": True})
    
    db.commit()
    return org

def delete_organization(db: Session, org_id: UUID):
    org = get_organization_by_id(db, org_id)
    if not org:
        raise Exception("Organization not found")
    
    db.delete(org)
    db.commit()
    return True
