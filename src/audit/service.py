from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from src.audit.models import AuditLog
from src.audit import exceptions as audit_exceptions
from src.exceptions import APIException


def log_audit(
    db: Session,
    organization_id: UUID,
    action: str,
    target_id: Optional[UUID] = None,
    changes: Optional[dict] = None,
    actor_id: Optional[UUID] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """
    Creates and persists an audit log entry in the database.

    Args:
        db (Session): The active database session.
        organization_id (UUID): The organization ID associated with the log.
        action (str): The activity or action being logged.
        target_id (Optional[UUID], optional): The ID of the target resource affected. Defaults to None.
        changes (Optional[dict], optional): Dictionary detailing the old/new changes. Defaults to None.
        actor_id (Optional[UUID], optional): The ID of the user performing the action. Defaults to None.
        ip_address (Optional[str], optional): The client's IP address. Defaults to None.

    Returns:
        AuditLog: The persisted audit log database object.

    Raises:
        APIException: If any API level exception is encountered during saving.
        AuditLogError: If any database error occurs during saving.
    """

    log = AuditLog(
        organization_id=organization_id,
        actor_id=actor_id,
        target_id=target_id,
        action=action,
        changes=changes,
        ip_address=ip_address,
    )

    try:
        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    except APIException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise audit_exceptions.AuditLogError(str(e))


def get_audit_logs(
    db: Session,
    organization_id: UUID,
    target_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Retrieves audit log entries for a given organization with optional filtering.

    Args:
        db (Session): The active database session.
        organization_id (UUID): The organization ID to filter logs for.
        target_id (Optional[UUID], optional): Optional target resource ID filter. Defaults to None.
        skip (int, optional): The number of records to skip for pagination. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[AuditLog]: A list of AuditLog database models matching the filters.
    """

    query = db.query(AuditLog).filter(AuditLog.organization_id == organization_id)

    if target_id:
        query = query.filter(AuditLog.target_id == target_id)

    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
