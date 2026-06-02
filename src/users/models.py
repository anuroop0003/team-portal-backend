import uuid
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.database import Base


class User(Base):
    __tablename__ = "users"

    # Core Identity
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # HR Essentials
    employee_id: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )  # Set to nullable=True for existing users
    department: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    date_of_joining: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Personal Details
    gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Status & Timestamps
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Reset Password Token
    reset_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    statutory_details: Mapped[Optional["EmployeeStatutory"]] = relationship(
        "EmployeeStatutory", back_populates="user", uselist=False
    )
    memberships: Mapped[List["Membership"]] = relationship(
        "Membership", back_populates="user", cascade="all, delete-orphan"
    )
    organizations: Mapped[List["Organization"]] = relationship(
        "Organization", secondary="memberships", viewonly=True
    )

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
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String, nullable=False, default="EMPLOYEE"
    )  # e.g., 'OWNER', 'ADMIN', 'EMPLOYEE'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="memberships"
    )


class EmployeeStatutory(Base):
    __tablename__ = "employee_statutory"

    # Core Identity
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Financial/Statutory PII
    pan_number: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True
    )
    aadhar_number: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True
    )
    bank_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ifsc_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationship back to user
    user: Mapped["User"] = relationship("User", back_populates="statutory_details")
