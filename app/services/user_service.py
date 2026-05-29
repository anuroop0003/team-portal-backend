from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
import secrets
import string
import uuid
from app.models.user_model import User, Membership
from app.models.statutory_model import EmployeeStatutory
from app.models.organization_model import Organization
from app.models.audit_model import AuditLog
from app.core.security import hash_password


# -------- Helpers --------
def log_audit(
    db: Session,
    organization_id: UUID,
    action: str,
    target_id: UUID = None,
    changes: dict = None,
    actor_id: UUID = None,
    ip_address: str = None,
):
    log = AuditLog(
        organization_id=organization_id,
        actor_id=actor_id,
        target_id=target_id,
        action=action,
        changes=changes,
        ip_address=ip_address,
    )
    db.add(log)


# -------- Create User --------
def create_user(db: Session, user_data, role: str = "EMPLOYEE", ip_address: str = None):
    existing = db.query(User).filter(User.email == user_data.email).first()

    # If user doesn't exist, create them
    if not existing:
        # Fetch Organization for ID generation
        org = (
            db.query(Organization)
            .filter(Organization.id == user_data.organization_id)
            .first()
        )
        if not org:
            raise Exception("Organization not found")

        # Generate Employee ID
        user_count = (
            db.query(func.count(Membership.id))
            .filter(Membership.organization_id == user_data.organization_id)
            .scalar()
        )
        employee_id = f"{org.code}-{user_count + 1:04d}"

        # Handle Invitation Flow
        password = user_data.password
        if not password:
            # Generate random 16 character strong password for the DB
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = "".join(secrets.choice(alphabet) for i in range(16))

        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=hash_password(password),
            employee_id=employee_id,
            designation=user_data.designation,
            department=user_data.department,
            date_of_joining=user_data.date_of_joining,
            gender=user_data.gender,
            date_of_birth=user_data.date_of_birth,
            blood_group=user_data.blood_group,
            emergency_contact=user_data.emergency_contact,
        )

        db.add(new_user)
        db.flush()

        # Create empty Statutory Record
        new_statutory = EmployeeStatutory(user_id=new_user.id)
        db.add(new_statutory)

        user = new_user
    else:
        user = existing
        # Check if already a member of this organization
        membership_exists = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id,
                Membership.organization_id == user_data.organization_id,
            )
            .first()
        )
        if membership_exists:
            raise Exception("User is already a member of this organization")

    # Create Membership
    db.add(
        Membership(
            user_id=user.id, organization_id=user_data.organization_id, role=role
        )
    )

    # Audit Log
    log_audit(
        db,
        user_data.organization_id,
        "CREATE_USER",
        target_id=user.id,
        ip_address=ip_address,
    )

    db.flush()
    db.refresh(user)

    return user


# -------- Get All Users --------
def get_users(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
):
    query = (
        db.query(User)
        .join(Membership)
        .filter(Membership.organization_id == organization_id)
    )

    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
            | (User.employee_id.ilike(f"%{search}%"))
        )

    return query.offset(skip).limit(limit).all()


# -------- Get User By ID --------
def get_user_by_id(db: Session, user_id: UUID, organization_id: UUID = None):
    query = db.query(User).filter(User.id == user_id)
    if organization_id:
        query = query.join(Membership).filter(
            Membership.organization_id == organization_id
        )
    return query.first()


# -------- User Soft Delete (Deactivate) --------
def deactivate_user(db: Session, user_id: UUID, organization_id: UUID):
    user = get_user_by_id(db, user_id, organization_id)
    if not user:
        raise Exception("User not found in this organization")

    user.is_active = False
    db.commit()
    return user


# -------- Update User --------
def update_user(
    db: Session,
    user_id: UUID,
    organization_id: UUID,
    update_data: dict,
    ip_address: str = None,
):
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
        log_audit(
            db,
            organization_id,
            "UPDATE_USER",
            target_id=user.id,
            changes=audit_changes,
            ip_address=ip_address,
        )

    db.commit()
    db.refresh(user)
    return user


# -------- Hard Delete User --------
def delete_user(
    db: Session, user_id: UUID, organization_id: UUID, ip_address: str = None
):
    user = get_user_by_id(db, user_id, organization_id)
    if not user:
        raise Exception("User not found in this organization")

    # Protection: Ensure at least one admin exists
    # Find the user's membership for this org
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == user_id, Membership.organization_id == organization_id
        )
        .first()
    )

    if membership.role.lower() in ["admin", "owner"]:
        admin_count = (
            db.query(func.count(Membership.id))
            .filter(
                Membership.role.ilike("admin") | Membership.role.ilike("owner"),
                Membership.organization_id == organization_id,
            )
            .scalar()
        )
        if admin_count <= 1:
            raise Exception("Cannot delete the last administrator/owner")

    log_audit(
        db, organization_id, "DELETE_USER", target_id=user.id, ip_address=ip_address
    )
    # Note: We should probably only delete the membership unless they want to delete the user entirely
    # For now, following original logic of deleting User entirely
    db.delete(user)
    db.commit()
    return True
