import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class EmployeeStatutory(Base):
    __tablename__ = "employee_statutory"

    # Core Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Financial/Statutory PII
    pan_number = Column(String, unique=True, nullable=True)
    aadhar_number = Column(String, unique=True, nullable=True)
    bank_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)

    # Relationship back to user
    user = relationship("User", back_populates="statutory_details")
