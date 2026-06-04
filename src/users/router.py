from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.users.schemas import CreateUser, UserResponse, UserDetailResponse, UserUpdate
from src.users import service as user_service
from src.auth import service as auth_service
from src.audit.dependencies import audit_logger, set_audit_event

user_router = APIRouter(prefix="/users", tags=["Users"])
admin_router = APIRouter(prefix="/admins", tags=["Admin Management"])


@user_router.post(
    "/", response_model=UserDetailResponse, dependencies=[Depends(audit_logger)]
)
async def create_user(
    request: Request, user: CreateUser, db: Session = Depends(get_db)
):
    """
    Create a new user under an organization, optionally triggering the invitation flow.

    Args:
        request (Request): The incoming request for auditing and IP context.
        user (CreateUser): The data required to create a new user.
        db (Session): The database session dependency.

    Returns:
        UserDetailResponse: Details of the newly created user.
    """

    res = await auth_service.invite_user_workflow(
        db, user, role="EMPLOYEE", ip_address=request.client.host
    )

    set_audit_event(request, user.organization_id, "CREATE_USER", res.id)

    return res


@user_router.get("/", response_model=list[UserResponse])
def get_users(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve all users belonging to a specific organization.

    Args:
        organization_id (UUID): The unique ID of the organization.
        skip (int, optional): The number of records to skip for pagination. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.
        search (str, optional): A search string to filter users by name, email, or employee ID. Defaults to None.
        db (Session): The database session dependency.

    Returns:
        list[UserResponse]: A list of users matching the filter criteria.
    """

    return user_service.get_users(db, organization_id, skip, limit, search)


@user_router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: UUID, organization_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific user within an organization.

    Args:
        user_id (UUID): The unique ID of the user.
        organization_id (UUID): The unique ID of the organization.
        db (Session): The database session dependency.

    Returns:
        UserDetailResponse: Details of the user.
    """

    return user_service.get_user_by_id(db, user_id, organization_id)


@admin_router.get("/", response_model=list[UserDetailResponse])
def list_admins(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
):
    """
    List all administrators in a specific organization.

    Args:
        organization_id (UUID): The unique ID of the organization.
        skip (int, optional): The number of records to skip for pagination. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.
        search (str, optional): Search string to filter administrators by name, email, or employee ID. Defaults to None.
        db (Session): The database session dependency.

    Returns:
        list[UserDetailResponse]: A list of administrators.
    """

    return user_service.get_users(db, organization_id, skip, limit, search)


@admin_router.post(
    "/", response_model=UserDetailResponse, dependencies=[Depends(audit_logger)]
)
async def create_admin(
    request: Request, admin: CreateUser, db: Session = Depends(get_db)
):
    """
    Create a new administrator under an organization.

    Args:
        request (Request): The incoming request for auditing and IP context.
        admin (CreateUser): The data required to create a new administrator.
        db (Session): The database session dependency.

    Returns:
        UserDetailResponse: Details of the newly created admin.
    """

    res = await auth_service.invite_user_workflow(
        db, admin, role="admin", ip_address=request.client.host
    )

    set_audit_event(request, admin.organization_id, "CREATE_USER", res.id)

    return res


@admin_router.put(
    "/{user_id}",
    response_model=UserDetailResponse,
    dependencies=[Depends(audit_logger)],
)
def update_user(
    request: Request,
    user_id: UUID,
    organization_id: UUID,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
):
    """
    Update details of a user.

    Args:
        request (Request): The incoming request for auditing and IP context.
        user_id (UUID): The unique ID of the user to update.
        organization_id (UUID): The unique ID of the organization.
        update_data (UserUpdate): The data fields to update.
        db (Session): The database session dependency.

    Returns:
        UserDetailResponse: The updated user details.
    """

    res = user_service.update_user(
        db,
        user_id,
        organization_id,
        update_data.model_dump(exclude_unset=True),
        ip_address=request.client.host,
    )

    set_audit_event(
        request,
        organization_id,
        "UPDATE_USER",
        res.id,
        changes=getattr(res, "audit_changes", None),
    )

    return res


@admin_router.post("/{user_id}/deactivate", dependencies=[Depends(audit_logger)])
def deactivate_user(
    request: Request,
    user_id: UUID,
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Deactivate a user.

    Args:
        request (Request): The incoming request for auditing.
        user_id (UUID): The unique ID of the user to deactivate.
        organization_id (UUID): The unique ID of the organization.
        db (Session): The database session dependency.

    Returns:
        dict: A success message payload.
    """

    res = user_service.deactivate_user(db, user_id, organization_id)

    set_audit_event(request, organization_id, "DEACTIVATE_USER", user_id)

    return res


@admin_router.delete("/{user_id}", dependencies=[Depends(audit_logger)])
def delete_user(
    request: Request,
    user_id: UUID,
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a user.

    Args:
        request (Request): The incoming request for auditing and IP context.
        user_id (UUID): The unique ID of the user to delete.
        organization_id (UUID): The unique ID of the organization.
        db (Session): The database session dependency.

    Returns:
        dict: A success message payload.
    """

    res = user_service.delete_user(
        db, user_id, organization_id, ip_address=request.client.host
    )

    set_audit_event(request, organization_id, "DELETE_USER", user_id)

    return res
