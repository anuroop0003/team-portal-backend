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

class AdminSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str

class OrganizationSignUp(BaseModel):
    name: str
    initial: str
    full_name: Optional[str] = None
    logo_url: Optional[str] = None

class OrganizationSignUpRequest(BaseModel):
    organization: OrganizationSignUp
    admin: AdminSignUp

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class AuthMeResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    organization_id: Optional[UUID] = None
    is_verified: bool

    class Config:
        from_attributes = True
