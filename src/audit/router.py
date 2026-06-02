from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.audit import service as audit_service
from src.audit.schemas import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit & Compliance"])


@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    organization_id: UUID,
    target_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Retrieve audit logs for a specific organization, optionally filtered by target ID.

    Args:
        organization_id (UUID): The unique ID of the organization.
        target_id (Optional[UUID], optional): Filter logs by the target resource ID. Defaults to None.
        skip (int, optional): The number of records to skip for pagination. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.
        db (Session): The database session dependency.

    Returns:
        List[AuditLogResponse]: A list of audit log records.
    """

    return audit_service.get_audit_logs(
        db=db,
        organization_id=organization_id,
        target_id=target_id,
        skip=skip,
        limit=limit,
    )
