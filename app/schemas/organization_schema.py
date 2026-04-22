from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    code: str = Field(..., validation_alias="code")
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
