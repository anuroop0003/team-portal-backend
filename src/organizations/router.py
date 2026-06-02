from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.organizations.schemas import OrganizationCreate, OrganizationResponse
from src.organizations import service as organization_service
from src.audit.dependencies import audit_logger, set_audit_event

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "/", response_model=OrganizationResponse, dependencies=[Depends(audit_logger)]
)
def create_organization(
    request: Request, org: OrganizationCreate, db: Session = Depends(get_db)
):
    """
    Create a new organization with the provided details.

    Args:
        request (Request): The incoming request for setting audit events.
        org (OrganizationCreate): The organization details schema.
        db (Session): The database session dependency.

    Returns:
        OrganizationResponse: The details of the created organization.
    """

    res = organization_service.create_organization(db, org)

    set_audit_event(request, res.id, "CREATE_ORGANIZATION", res.id)

    return res


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    """
    Retrieve all registered organizations.

    Args:
        db (Session): The database session dependency.

    Returns:
        list[OrganizationResponse]: A list of all organizations.
    """

    return organization_service.get_organizations(db)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific organization by its ID.

    Args:
        org_id (UUID): The unique ID of the organization.
        db (Session): The database session dependency.

    Returns:
        OrganizationResponse: The details of the requested organization.
    """

    return organization_service.get_organization_by_id(db, org_id)


@router.patch(
    "/{org_id}/suspend",
    response_model=OrganizationResponse,
    dependencies=[Depends(audit_logger)],
)
def suspend_organization(request: Request, org_id: UUID, db: Session = Depends(get_db)):
    """
    Suspend an organization and deactivate all its associated users.

    Args:
        request (Request): The incoming request for auditing.
        org_id (UUID): The unique ID of the organization to suspend.
        db (Session): The database session dependency.

    Returns:
        OrganizationResponse: The updated details of the suspended organization.
    """

    res = organization_service.suspend_organization(db, org_id)

    set_audit_event(request, org_id, "SUSPEND_ORGANIZATION", org_id)

    return res


@router.patch(
    "/{org_id}/unsuspend",
    response_model=OrganizationResponse,
    dependencies=[Depends(audit_logger)],
)
def unsuspend_organization(
    request: Request, org_id: UUID, db: Session = Depends(get_db)
):
    """
    Unsuspend an organization and reactivate all its associated users.

    Args:
        request (Request): The incoming request for auditing.
        org_id (UUID): The unique ID of the organization to unsuspend.
        db (Session): The database session dependency.

    Returns:
        OrganizationResponse: The updated details of the reactivated organization.
    """

    res = organization_service.unsuspend_organization(db, org_id)

    set_audit_event(request, org_id, "UNSUSPEND_ORGANIZATION", org_id)

    return res


@router.delete("/{org_id}", dependencies=[Depends(audit_logger)])
def delete_organization(request: Request, org_id: UUID, db: Session = Depends(get_db)):
    """
    Permanently delete an organization and all its database references.

    Args:
        request (Request): The incoming request for auditing.
        org_id (UUID): The unique ID of the organization to delete.
        db (Session): The database session dependency.

    Returns:
        dict: A success message payload.
    """

    res = organization_service.delete_organization(db, org_id)

    set_audit_event(request, org_id, "DELETE_ORGANIZATION", org_id)

    return res
