from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import CreateUser, UserResponse, UserDetailResponse
from app.controllers import user_controller

router = APIRouter(prefix="/users", tags=["Users"])

# -------- Create User --------
@router.post("/", response_model=UserDetailResponse)
async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    try:
        return await user_controller.create_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------- Get All Users --------
@router.get("/", response_model=list[UserResponse])
def get_users(organization_id: UUID, skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    return user_controller.get_users(db, organization_id, skip, limit, search)


# -------- Get User By ID --------
@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: UUID, organization_id: UUID, db: Session = Depends(get_db)):
    user = user_controller.get_user_by_id(db, user_id, organization_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user