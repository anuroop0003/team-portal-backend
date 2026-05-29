import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    # Core Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    designation = Column(String, nullable=True)

    # HR Essentials
    employee_id = Column(
        String, unique=True, index=True, nullable=True
    )  # Set to nullable=True for existing users
    department = Column(String, nullable=True)
    date_of_joining = Column(Date, nullable=True)

    # Personal Details
    gender = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    blood_group = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)

    # Status & Timestamps
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    statutory_details = relationship(
        "EmployeeStatutory", back_populates="user", uselist=False
    )
    memberships = relationship(
        "Membership", back_populates="user", cascade="all, delete-orphan"
    )
    organizations = relationship("Organization", secondary="memberships", viewonly=True)

    @property
    def role(self):
        if self.memberships:
            return self.memberships[0].role
        return "EMPLOYEE"

    @property
    def organization_id(self):
        if self.memberships:
            return self.memberships[0].organization_id
        return None


class Membership(Base):
    __tablename__ = "memberships"

    # Core Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(
        String, nullable=False, default="EMPLOYEE"
    )  # e.g., 'OWNER', 'ADMIN', 'EMPLOYEE'
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")
