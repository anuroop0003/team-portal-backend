from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AdminRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    job_title: Optional[str] = None

class OrganizationRegister(BaseModel):
    name: str
    code: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None

class OrganizationRegisterRequest(BaseModel):
    organization: OrganizationRegister
    admin: AdminRegister

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class SendVerificationRequest(BaseModel):
    email: EmailStr

class AuthMeResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    organization_id: Optional[UUID] = None
    is_verified: bool

    class Config:
        from_attributes = True

class VerifyTokenInfoResponse(BaseModel):
    email: EmailStr
    is_valid: bool
