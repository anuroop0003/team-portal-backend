from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import CreateUser, UserResponse
from app.controllers import user_controller

router = APIRouter(prefix="/users", tags=["Users"])

# -------- Create User --------
@router.post("/", response_model=UserResponse)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    try:
        return user_controller.create_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------- Get All Users --------
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return user_controller.get_users(db)


# -------- Get User By ID --------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_controller.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# -------- Deactivate User --------
@router.patch("/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = user_controller.deactivate_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deactivated"}