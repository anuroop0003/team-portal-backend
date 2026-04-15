from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import CreateUser, UserDetailResponse, UserUpdate
from app.controllers import user_controller

router = APIRouter(prefix="/admins", tags=["Admin Management"])

# -------- List All Admins/Employees --------
@router.get("/", response_model=list[UserDetailResponse])
def list_admins(organization_id: UUID, skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    return user_controller.get_users(db, organization_id, skip, limit, search)

# -------- Create Admin --------
@router.post("/", response_model=UserDetailResponse)
def create_admin(admin: CreateUser, db: Session = Depends(get_db)):
    try:
        # Override role to admin
        admin.role = "admin"
        return user_controller.create_user(db, admin)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------- Edit Admin/User --------
@router.put("/{user_id}", response_model=UserDetailResponse)
def update_user(user_id: UUID, organization_id: UUID, update_data: UserUpdate, db: Session = Depends(get_db)):
    try:
        return user_controller.update_user(db, user_id, organization_id, update_data.model_dump(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------- Deactivate User (Soft Delete) --------
@router.post("/{user_id}/deactivate")
def deactivate_user(user_id: UUID, organization_id: UUID, db: Session = Depends(get_db)):
    try:
        user_controller.deactivate_user(db, user_id, organization_id)
        return {"message": "User account deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------- Hard Delete Admin/User --------
@router.delete("/{user_id}")
def delete_user(user_id: UUID, organization_id: UUID, db: Session = Depends(get_db)):
    try:
        user_controller.delete_user(db, user_id, organization_id)
        return {"message": f"User {user_id} and associated data deleted successfully (Hard Delete)"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
