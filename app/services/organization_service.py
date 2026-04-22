from uuid import UUID
from sqlalchemy.orm import Session
from app.models.organization_model import Organization

def create_organization(db: Session, org_data):
    # Check Existance
    existing_code = db.query(Organization).filter(Organization.code == org_data.code).first()
    
    if existing_code:
        raise Exception("Organization with this code already exists")
    
    new_org = Organization(
        name=org_data.name,
        code=org_data.code,
        logo_url=org_data.logo_url,
        website_url=org_data.website_url,
        industry=org_data.industry,
        company_size=org_data.company_size
    )
    
    db.add(new_org)
    db.flush() # Use flush instead of commit to keep transaction open
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
