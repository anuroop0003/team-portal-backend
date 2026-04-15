import uuid
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # Who performed the action
    target_id = Column(UUID(as_uuid=True), nullable=True) # ID of the record being changed (User ID, etc.)
    
    action = Column(String, nullable=False) # e.g., 'CREATE_USER', 'UPDATE_CORE_IDENTITY', 'DELETE_USER'
    changes = Column(JSON, nullable=True) # Stores Old/New values: {"field": {"old": "x", "new": "y"}}
    ip_address = Column(String, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
