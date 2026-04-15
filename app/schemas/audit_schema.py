from uuid import UUID
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: UUID
    organization_id: UUID
    actor_id: Optional[UUID]
    target_id: Optional[UUID]
    action: str
    changes: Optional[Any]
    timestamp: datetime

    class Config:
        from_attributes = True
