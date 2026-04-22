from fastapi import Request
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user_model import User, Membership
from app.schemas.auth_schema import (
    SignInRequest, Token, OrganizationRegisterRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    AuthMeResponse, SendVerificationRequest, VerifyTokenInfoResponse
)
from app.schemas.user_schema import CreateUser
from app.services import auth_service, user_service, organization_service
from app.core.security import verify_password
from app.core.config import settings
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])

# -----------------------------
# 🔹 Helpers
# -----------------------------
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Removed get_user_by_verification_token since we use JWT now

def get_user_by_reset_token(db: Session, token: str):
    return db.query(User).filter(User.reset_token == token).first()

# -----------------------------
# 🔹 Register Organization
# -----------------------------
@router.post("/register-organization", response_model=AuthMeResponse)
async def register_organization(
    request: Request,
    payload: OrganizationRegisterRequest,
    db: Session = Depends(get_db)
):
    if get_user_by_email(db, payload.admin.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        org = organization_service.create_organization(
            db, payload.organization
        )

        user = user_service.create_user(
            db,
            CreateUser(
                name=payload.admin.name,
                email=payload.admin.email,
                password=payload.admin.password,
                phone=payload.admin.phone,
                designation=payload.admin.job_title,
                organization_id=org.id
            ),
            role="OWNER",
            ip_address=request.client.host
        )

        db.commit()
        db.refresh(user)

        return user

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed")


# -----------------------------
# 🔹 Sign In
# -----------------------------
@router.post("/sign-in", response_model=Token)
def sign_in(request: Request, credentials: SignInRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, credentials.email)

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

    token = auth_service.create_access_token(
        data={"sub": user.email, "id": str(user.id)}
    )

    user_service.log_audit(db, user.organization_id, "SIGN_IN", actor_id=user.id, ip_address=request.client.host)

    return {"access_token": token, "token_type": "bearer"}


# -----------------------------
# 🔹 Email Verification
# -----------------------------
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None or payload.get("type") != "verification":
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}



@router.get("/verify-token-info", response_model=VerifyTokenInfoResponse)
def verify_token_info(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None or payload.get("type") != "verification":
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    return {"email": user.email, "is_valid": True}



# -----------------------------
# 🔹 Send Verification Email
# -----------------------------
@router.post("/send-verification")
async def send_verification(payload: SendVerificationRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)

    if not user:
        return {"message": "If an account exists, a verification link was sent"}

    if user.is_verified:
        return {"message": "Email is already verified"}

    await auth_service.send_verification_email(user.email)

    return {"message": "Verification email sent"}


# -----------------------------
# 🔹 Forgot Password
# -----------------------------
@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)

    if user:
        user.reset_token = str(uuid.uuid4())
        db.commit()
        await auth_service.send_reset_password_email(user.email, user.reset_token)

    return {"message": "If an account exists, a reset link was sent"}


# -----------------------------
# 🔹 Reset Password
# -----------------------------
@router.post("/reset-password")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = get_user_by_reset_token(db, payload.token)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = user_service.hash_password(payload.new_password)
    user.reset_token = None
    db.commit()

    user_service.log_audit(db, user.organization_id, "RESET_PASSWORD", target_id=user.id, ip_address=request.client.host)

    return {"message": "Password reset successfully"}


# -----------------------------
# 🔹 Current User
# -----------------------------
@router.get("/me", response_model=AuthMeResponse)
def get_me(current_user: User = Depends(auth_service.get_current_active_user)):
    return current_user