from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.users.models import User, Membership, EmployeeStatutory
from src.organizations.models import Organization
from src.auth.utils import hash_password
from src.users import exceptions as user_exceptions
from src.organizations.exceptions import OrganizationNotFoundError
from src.users import constants as user_constants
from src.users.utils import generate_random_password


async def create_user(
    db: Session, user_data, role: str = "EMPLOYEE", ip_address: str = None
):
    """
    Creates a new user record and sets up their initial membership and statutory records.

    Args:
        db (Session): The active database session.
        user_data: The data representation for the user to be created.
        role (str, optional): The initial role to allocate. Defaults to "EMPLOYEE".
        ip_address (str, optional): The client's IP address. Defaults to None.

    Returns:
        User: The created User database model instance.

    Raises:
        OrganizationNotFoundError: If the organization ID in user_data is invalid.
        UserAlreadyMemberError: If a membership already exists for the email and organization.
    """

    existing = db.query(User).filter(User.email == user_data.email).first()

    if not existing:
        org = (
            db.query(Organization)
            .filter(Organization.id == user_data.organization_id)
            .first()
        )

        if not org:
            raise OrganizationNotFoundError()

        user_count = (
            db.query(func.count(Membership.id))
            .filter(Membership.organization_id == user_data.organization_id)
            .scalar()
        )

        employee_id = f"{org.code}-{user_count + 1:04d}"

        password = user_data.password
        has_no_password = not password

        if has_no_password:
            password = generate_random_password()

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

        new_statutory = EmployeeStatutory(user_id=new_user.id)

        db.add(new_statutory)

        user = new_user

    else:
        user = existing

        membership_exists = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id,
                Membership.organization_id == user_data.organization_id,
            )
            .first()
        )

        if membership_exists:
            raise user_exceptions.UserAlreadyMemberError()

    db.add(
        Membership(
            user_id=user.id, organization_id=user_data.organization_id, role=role
        )
    )

    db.flush()
    db.refresh(user)

    return user


def get_users(
    db: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
):
    """
    Retrieves users within a specific organization with pagination and optional search filter.

    Args:
        db (Session): The active database session.
        organization_id (UUID): The organization ID.
        skip (int, optional): Number of users to skip. Defaults to 0.
        limit (int, optional): Maximum number of users to return. Defaults to 100.
        search (str, optional): Substring filter for user name, email, or employee ID. Defaults to None.

    Returns:
        List[User]: A list of matching User database models.
    """

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


def get_user_by_id(db: Session, user_id: UUID, organization_id: UUID = None):
    """
    Retrieves a single user by their unique ID, optionally matching organization membership.

    Args:
        db (Session): The active database session.
        user_id (UUID): The unique ID of the user.
        organization_id (UUID, optional): The organization ID filter. Defaults to None.

    Returns:
        User: The matching User database record.

    Raises:
        UserNotFoundError: If no matching user is found.
    """

    query = db.query(User).filter(User.id == user_id)

    if organization_id:
        query = query.join(Membership).filter(
            Membership.organization_id == organization_id
        )

    user = query.first()

    if not user:
        raise user_exceptions.UserNotFoundError()

    return user


def deactivate_user(db: Session, user_id: UUID, organization_id: UUID):
    """
    Deactivates a user account, setting is_active to False.

    Args:
        db (Session): The active database session.
        user_id (UUID): The unique ID of the user to deactivate.
        organization_id (UUID): The organization ID associated with the user.

    Returns:
        dict: A success message payload.

    Raises:
        UserNotFoundError: If the user doesn't exist.
    """

    user = get_user_by_id(db, user_id, organization_id)

    try:
        user.is_active = False

        db.commit()

        return {"message": user_constants.MSG_USER_DEACTIVATE_SUCCESS}

    except Exception:
        db.rollback()
        raise


def update_user(
    db: Session,
    user_id: UUID,
    organization_id: UUID,
    update_data: dict,
    ip_address: str = None,
):
    """
    Updates properties of an existing user and logs changes in the audit changes metadata.

    Args:
        db (Session): The active database session.
        user_id (UUID): The unique ID of the user.
        organization_id (UUID): The organization ID.
        update_data (dict): Key-value pairs representing fields to update.
        ip_address (str, optional): Client's IP address. Defaults to None.

    Returns:
        User: The updated User database model.
    """

    user = get_user_by_id(db, user_id, organization_id)

    try:
        audit_changes = {}

        for key, value in update_data.items():
            if value is not None:
                old_val = getattr(user, key)

                if old_val != value:
                    if key == "password":
                        audit_changes[key] = {"old": "****", "new": "****"}
                        setattr(user, "hashed_password", hash_password(value))

                    else:
                        audit_changes[key] = {"old": str(old_val), "new": str(value)}
                        setattr(user, key, value)

        db.commit()
        db.refresh(user)

        if audit_changes:
            user.audit_changes = audit_changes

        return user

    except Exception:
        db.rollback()
        raise


def delete_user(
    db: Session, user_id: UUID, organization_id: UUID, ip_address: str = None
):
    """
    Permanently deletes a user from the database.

    Args:
        db (Session): The active database session.
        user_id (UUID): The unique ID of the user to delete.
        organization_id (UUID): The organization ID.
        ip_address (str, optional): Client IP. Defaults to None.

    Returns:
        dict: A success message payload.

    Raises:
        LastAdminDeletionError: If attempting to delete the last administrator in the organization.
    """

    user = get_user_by_id(db, user_id, organization_id)

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
            raise user_exceptions.LastAdminDeletionError()

    try:
        db.delete(user)
        db.commit()

        return {"message": user_constants.MSG_USER_DELETED_SUCCESS.format(user_id)}

    except Exception:
        db.rollback()
        raise


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Fetches a user by their email address.

    Args:
        db (Session): The active database session.
        email (str): The email address to look up.

    Returns:
        User | None: The matching User or None.
    """

    return db.query(User).filter(User.email == email).first()


def get_user_by_reset_token(db: Session, token: str) -> User | None:
    """
    Fetches a user associated with the given password reset token.

    Args:
        db (Session): The active database session.
        token (str): The reset token UUID string.

    Returns:
        User | None: The matching User or None.
    """

    return db.query(User).filter(User.reset_token == token).first()


def deactivate_users_by_organization_id(db: Session, organization_id: UUID):
    """
    Bulk deactivates all users associated with a specific organization.

    Args:
        db (Session): The active database session.
        organization_id (UUID): The unique ID of the organization.
    """

    db.query(User).filter(
        User.id.in_(
            db.query(Membership.user_id).filter(
                Membership.organization_id == organization_id
            )
        )
    ).update({"is_active": False}, synchronize_session=False)


def reactivate_users_by_organization_id(db: Session, organization_id: UUID):
    """
    Bulk reactivates all users associated with a specific organization.

    Args:
        db (Session): The active database session.
        organization_id (UUID): The unique ID of the organization.
    """

    db.query(User).filter(
        User.id.in_(
            db.query(Membership.user_id).filter(
                Membership.organization_id == organization_id
            )
        )
    ).update({"is_active": True}, synchronize_session=False)
