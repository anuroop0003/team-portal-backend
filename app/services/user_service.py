from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user_model import User
from app.models.statutory_model import EmployeeStatutory
from app.models.organization_model import Organization
from app.models.audit_model import AuditLog
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------- Helpers --------
def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def log_audit(db: Session, organization_id: UUID, action: str, target_id: UUID = None, changes: dict = None, actor_id: UUID = None):
    log = AuditLog(
        organization_id=organization_id,
        actor_id=actor_id,
        target_id=target_id,
        action=action,
        changes=changes
    )
    db.add(log)
    # Note: We don't commit here, it will be committed by the calling service function with the main transaction.

# -------- Create User --------
def create_user(db:Session, user_data):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if(existing):
        raise Exception("User already exists")

    # Fetch Organization for initial
    org = db.query(Organization).filter(Organization.id == user_data.organization_id).first()
    if not org:
        raise Exception("Organization not found")

    # Generate Employee ID: {ORG_INITIAL}-{Sequence} (e.g., TP-0001)
    user_count = db.query(func.count(User.id)).filter(User.organization_id == user_data.organization_id).scalar()
    employee_id = f"{org.initial}-{user_count + 1:04d}"

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role,
        organization_id=user_data.organization_id,
        hashed_password=hash_password(user_data.password),
        employee_id=employee_id,
        # HR Identity
        designation=user_data.designation,
        department=user_data.department,
        date_of_joining=user_data.date_of_joining,
        gender=user_data.gender,
        date_of_birth=user_data.date_of_birth,
        blood_group=user_data.blood_group,
        emergency_contact=user_data.emergency_contact
    )

    db.add(new_user)
    db.flush() # Get user ID for statutory relationship

    # Create empty Statutory Record
    new_statutory = EmployeeStatutory(user_id=new_user.id)
    db.add(new_statutory)
    
    # Audit Log
    log_audit(db, new_user.organization_id, "CREATE_USER", target_id=new_user.id)
    
    db.commit()
    db.refresh(new_user)

    return new_user

# -------- Get All Users --------
def get_users(db:Session, organization_id: UUID, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(User).filter(User.organization_id == organization_id)
    
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%")) |
            (User.employee_id.ilike(f"%{search}%"))
        )
        
    return query.offset(skip).limit(limit).all()

# -------- Get User By ID --------
def get_user_by_id(db:Session, user_id:UUID, organization_id: UUID = None):
    query = db.query(User).filter(User.id == user_id)
    if organization_id:
        query = query.filter(User.organization_id == organization_id)
    return query.first()

# -------- User Soft Delete (Deactivate) --------
def deactivate_user(db:Session, user_id:UUID, organization_id: UUID):
    user = get_user_by_id(db, user_id, organization_id)
    if not user:
        raise Exception("User not found in this organization")

    user.is_active = False
    db.commit()
    return user

# -------- Update User --------
def update_user(db:Session, user_id:UUID, organization_id: UUID, update_data:dict):
    user = get_user_by_id(db, user_id, organization_id)
    if not user:
        raise Exception("User not found in this organization")

    audit_changes = {}
    for key, value in update_data.items():
        if value is not None:
            old_val = getattr(user, key)
            if old_val != value:
                # Sensitive fields like password shouldn't be logged in plain text
                if key == "password":
                    audit_changes[key] = {"old": "****", "new": "****"}
                    setattr(user, "hashed_password", hash_password(value))
                else:
                    # Robust handling of UUIDs vs Strings in Audit Logs
                    audit_changes[key] = {"old": str(old_val), "new": str(value)}
                    setattr(user, key, value)

    if audit_changes:
        log_audit(db, organization_id, "UPDATE_USER", target_id=user.id, changes=audit_changes)

    db.commit()
    db.refresh(user)
    return user

# -------- Hard Delete User --------
def delete_user(db:Session, user_id:UUID, organization_id: UUID):
    user = get_user_by_id(db, user_id, organization_id)
    if not user:
        raise Exception("User not found in this organization")

    # Protection: Ensure at least one admin exists
    if user.role == "admin":
        admin_count = db.query(func.count(User.id)).filter(User.role == "admin", User.organization_id == organization_id).scalar()
        if admin_count <= 1:
            raise Exception("Cannot delete the last administrator")

    log_audit(db, organization_id, "DELETE_USER", target_id=user.id)
    db.delete(user)
    db.commit()
    return True
