from pydantic import BaseModel, EmailStr
from typing import Optional

# -------- Create User --------
class CreateUser(BaseModel):
    name:str
    email:EmailStr
    phone:Optional[str] = None
    password: str
    role:Optional[str] = "employee"

# -------- Response --------
class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr
    phone:Optional[str]
    role:str
    is_active:bool

    class Config:
        from_attributes = True

# -------- Login --------
class UserLogin(BaseModel):
    email:EmailStr
    password:str
