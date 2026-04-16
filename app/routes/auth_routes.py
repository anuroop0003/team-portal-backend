import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user_model import User
from app.services import auth_service, user_service, organization_service
from app.schemas.auth_schema import (
    SignInRequest, Token, OrganizationSignUpRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, AuthMeResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register-organization", response_model=AuthMeResponse, summary="Enterprise Sign-Up (New Organization)")
async def sign_up(payload: OrganizationSignUpRequest, db: Session = Depends(get_db)):
    try:
        # 1. Create Organization
        org = organization_service.create_organization(db, payload.organization)
        
        # 2. Create Admin User
        # We need to adapt the payload for create_user
        user_data = payload.admin
        # Add necessary fields for user_service.create_user
        user_data_dict = user_data.model_dump()
        user_data_dict["role"] = "admin"
        user_data_dict["organization_id"] = org.id
        # We also need other fields from CreateUser but can set defaults
        # For simplicity, we'll manually create the user here or mock the object
        from app.schemas.user_schema import CreateUser
        user_create_data = CreateUser(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role="admin",
            organization_id=org.id
        )
        
        user = user_service.create_user(db, user_create_data)
        
        # 3. Generate verification token and send email
        verification_token = str(uuid.uuid4())
        user.verification_token = verification_token
        db.commit()
        
        await auth_service.send_verification_email(user.email, verification_token)
        
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sign-in", response_model=Token)
async def sign_in(credentials: SignInRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user_service.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")
    
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "id": str(user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        reset_token = str(uuid.uuid4())
        user.reset_token = reset_token
        db.commit()
        await auth_service.send_reset_password_email(user.email, reset_token)
    
    # Always return success to prevent email enumeration
    return {"message": "If an account with that email exists, we sent a reset link."}

@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user.hashed_password = user_service.hash_password(payload.new_password)
    user.reset_token = None
    db.commit()
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=AuthMeResponse)
async def get_me(current_user: User = Depends(auth_service.get_current_active_user)):
    return current_user
