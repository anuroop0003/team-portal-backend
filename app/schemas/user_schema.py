from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# -------- Create User --------
class CreateUser(BaseModel):
    name:str
    email:EmailStr
    designation: str
    password: Optional[str] = None
    phone:Optional[str] = None
    organization_id: Optional[UUID] = None

    # HR Identity Fields (Optional during creation)
    department: Optional[str] = None
    date_of_joining: Optional[date] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

# -------- Update User --------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    # HR Identity
    designation: Optional[str] = None
    department: Optional[str] = None
    date_of_joining: Optional[date] = None
    
    # Personal Details
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

# -------- Response --------
class UserResponse(BaseModel):
    id:UUID
    name:str
    email:EmailStr
    phone:Optional[str]
    role:str
    is_active:bool

    # HR Identity
    employee_id: Optional[str]
    designation: Optional[str]
    department: Optional[str]
    date_of_joining: Optional[date]
    gender: Optional[str]
    date_of_birth: Optional[date]
    blood_group: Optional[str]
    emergency_contact: Optional[str]

    class Config:
        from_attributes = True

# -------- Statutory Details --------
class StatutoryBase(BaseModel):
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None

class StatutoryResponse(StatutoryBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True

# -------- Nested Response --------
class UserDetailResponse(UserResponse):
    statutory_details: Optional[StatutoryResponse] = None

# -------- Login --------
class UserLogin(BaseModel):
    email:EmailStr
    password:str
