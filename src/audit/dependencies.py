from fastapi import Request, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.audit.service import log_audit
from uuid import UUID


def set_audit_event(
    request: Request,
    organization_id: UUID,
    action: str,
    target_id: UUID,
    changes: dict = None,
    actor_id: UUID = None,
):
    """
    Helper to set the audit event metadata on the request state.

    Args:
        request (Request): The incoming FastAPI request instance.
        organization_id (UUID): The unique ID of the organization associated with the event.
        action (str): The name/type of action performed (e.g. USER_LOGIN).
        target_id (UUID): The unique ID of the resource targeted by the action.
        changes (dict, optional): A dictionary of changed fields and their old/new values. Defaults to None.
        actor_id (UUID, optional): The unique ID of the user performing the action. Defaults to None.
    """

    request.state.audit_event = {
        "organization_id": organization_id,
        "action": action,
        "target_id": target_id,
        "changes": changes,
        "actor_id": actor_id,
    }


async def audit_logger(request: Request, db: Session = Depends(get_db)):
    """
    Generator dependency to write audit logs post-request execution.

    Args:
        request (Request): The incoming FastAPI request instance.
        db (Session): The SQLAlchemy database session dependency.

    Yields:
        None: Yields control back to the route handler first, then logs the event after completion.
    """

    yield

    if hasattr(request.state, "audit_event"):
        event = request.state.audit_event
        log_audit(
            db=db,
            organization_id=event["organization_id"],
            action=event["action"],
            target_id=event.get("target_id"),
            changes=event.get("changes"),
            actor_id=event.get("actor_id"),
            ip_address=request.client.host if request.client else None,
        )
