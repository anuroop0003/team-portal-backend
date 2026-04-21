import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user_model import User
from app.services import auth_service, user_service, organization_service
from app.schemas.auth_schema import (
    SignInRequest, Token, OrganizationRegisterRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, AuthMeResponse, SendVerificationRequest, VerifyTokenInfoResponse
)
from app.core.security import verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register-organization", response_model=AuthMeResponse, summary="Enterprise Register Organization")
async def register_organization(payload: OrganizationRegisterRequest, db: Session = Depends(get_db)):
    # 1. Validation
    
    # Check email uniqueness
    existing_user = db.query(User).filter(User.email == payload.admin.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        from app.utils.slugify import generate_unique_slug
        from app.models.user_model import Membership
        
        # 2. Generate Slug
        slug = generate_unique_slug(db, payload.organization.name)
        
        # 3. Create Organization (Atomic)
        org = organization_service.create_organization(db, payload.organization, slug)
        
        # 4. Create Admin User
        from app.schemas.user_schema import CreateUser
        user_create_data = CreateUser(
            name=payload.admin.name,
            email=payload.admin.email,
            password=payload.admin.password,
            phone=payload.admin.phone,
            designation=payload.admin.job_title,
            role="OWNER", # SaaS Standard
            organization_id=org.id
        )
        
        user = user_service.create_user(db, user_create_data)
        
        # 5. Create Membership Record
        membership = Membership(
            user_id=user.id,
            organization_id=org.id,
            role="OWNER"
        )
        db.add(membership)
        
        # 6. Verification Token
        verification_token = str(uuid.uuid4())
        user.verification_token = verification_token
        
        # FINAL COMMIT (Atomic)
        db.commit()
        db.refresh(user)
        
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sign-in", response_model=Token)
def sign_in(credentials: SignInRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400, 
            detail={"code": "ACCOUNT_DEACTIVATED", "message": "Account is deactivated"}
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=403, 
            detail={"code": "EMAIL_NOT_VERIFIED", "message": "Email not verified"}
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "id": str(user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}

@router.get("/verify-token-info", response_model=VerifyTokenInfoResponse)
def verify_token_info(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    return {"email": user.email, "is_valid": True}

@router.post("/send-verification")
async def send_verification(payload: SendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Return success to prevent email enumeration
        return {"message": "If an account with that email exists, we sent a verification link."}
    
    if user.is_verified:
        return {"message": "Email is already verified"}
    
    # Generate new token
    verification_token = str(uuid.uuid4())
    user.verification_token = verification_token
    db.commit()
    
    await auth_service.send_verification_email(user.email, verification_token)
    return {"message": "Verification email sent"}

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
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user.hashed_password = user_service.hash_password(payload.new_password)
    user.reset_token = None
    db.commit()
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=AuthMeResponse)
def get_me(current_user: User = Depends(auth_service.get_current_active_user)):
    return current_user
