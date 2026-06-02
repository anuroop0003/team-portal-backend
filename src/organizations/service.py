from uuid import UUID
from sqlalchemy.orm import Session
from src.organizations.models import Organization
from src.organizations import exceptions as org_exceptions
from src.organizations import constants as org_constants
from src.users import service as user_service


def create_organization(db: Session, org_data):
    """
    Creates a new organization in the database if it doesn't already exist.

    Args:
        db (Session): The active database session.
        org_data (OrganizationCreate): The data schema representing the new organization.

    Returns:
        Organization: The newly created organization instance.

    Raises:
        OrganizationAlreadyExistsError: If an organization with the same code already exists.
    """

    existing_code = (
        db.query(Organization).filter(Organization.code == org_data.code).first()
    )

    if existing_code:
        raise org_exceptions.OrganizationAlreadyExistsError()

    new_org = Organization(
        name=org_data.name,
        code=org_data.code,
        logo_url=org_data.logo_url,
        website_url=org_data.website_url,
        industry=org_data.industry,
        company_size=org_data.company_size,
    )

    db.add(new_org)
    db.flush()

    return new_org


def get_organizations(db: Session):
    """
    Retrieves all organization entries from the database.

    Args:
        db (Session): The active database session.

    Returns:
        List[Organization]: A list of all organization records.
    """

    return db.query(Organization).all()


def get_organization_by_id(db: Session, org_id: UUID):
    """
    Retrieves a single organization by its UUID.

    Args:
        db (Session): The active database session.
        org_id (UUID): The unique identifier of the organization.

    Returns:
        Organization: The matching organization database record.

    Raises:
        OrganizationNotFoundError: If no organization with the given ID exists.
    """

    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise org_exceptions.OrganizationNotFoundError()

    return org


def suspend_organization(db: Session, org_id: UUID):
    """
    Suspends an organization and deactivates all its associated users.

    Args:
        db (Session): The active database session.
        org_id (UUID): The unique identifier of the organization to suspend.

    Returns:
        Organization: The updated organization database record.

    Raises:
        OrganizationNotFoundError: If the organization does not exist.
    """

    org = get_organization_by_id(db, org_id)

    try:
        org.is_active = False

        user_service.deactivate_users_by_organization_id(db, org_id)

        db.commit()

        return org

    except Exception:
        db.rollback()
        raise


def unsuspend_organization(db: Session, org_id: UUID):
    """
    Unsuspends an organization and reactivates all its associated users.

    Args:
        db (Session): The active database session.
        org_id (UUID): The unique identifier of the organization to unsuspend.

    Returns:
        Organization: The updated organization database record.

    Raises:
        OrganizationNotFoundError: If the organization does not exist.
    """

    org = get_organization_by_id(db, org_id)

    try:
        org.is_active = True

        user_service.reactivate_users_by_organization_id(db, org_id)

        db.commit()

        return org

    except Exception:
        db.rollback()
        raise


def delete_organization(db: Session, org_id: UUID):
    """
    Deletes an organization record from the database.

    Args:
        db (Session): The active database session.
        org_id (UUID): The unique identifier of the organization to delete.

    Returns:
        dict: A success message payload.

    Raises:
        OrganizationNotFoundError: If the organization does not exist.
    """

    org = get_organization_by_id(db, org_id)

    try:
        db.delete(org)
        db.commit()

        return {
            "message": org_constants.MSG_ORGANIZATION_DELETED_SUCCESS.format(org_id)
        }

    except Exception:
        db.rollback()
        raise
