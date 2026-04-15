from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.audit_model import AuditLog
from app.schemas.audit_schema import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit & Compliance"])

@router.get("/", response_model=list[AuditLogResponse])
def get_audit_logs(
    organization_id: UUID, 
    target_id: Optional[UUID] = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog).filter(AuditLog.organization_id == organization_id)
    if target_id:
        query = query.filter(AuditLog.target_id == target_id)
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
