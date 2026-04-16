import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.auth_schema import TokenData

# OAuth2 settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Mail configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

# -------- JWT Logic --------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        if email is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_id=uuid.UUID(user_id))
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# -------- Email Logic --------

async def send_email(subject: str, recipient: str, body: str):
    # If mail settings are missing or default, log instead of failing in dev
    if not settings.MAIL_SERVER or settings.MAIL_SERVER in ["None", "smtp.example.com"] or not settings.MAIL_USERNAME or settings.MAIL_USERNAME == "placeholder@example.com":
        print(f"DEBUG EMAIL: To: {recipient} | Subject: {subject}")
        return

    try:
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            body=body,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"ERROR SENDING EMAIL: {e}")

async def send_verification_email(email: str, token: str):
    link = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    body = f"""
    <h1>Verify your email</h1>
    <p>Thank you for registering. Please click the link below to verify your account:</p>
    <p><a href="{link}">{link}</a></p>
    """
    await send_email("Verify your email", email, body)

async def send_reset_password_email(email: str, token: str):
    link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    body = f"""
    <h1>Reset your password</h1>
    <p>You requested a password reset. Please click the link below to set a new password:</p>
    <p><a href="{link}">{link}</a></p>
    """
    await send_email("Reset your password", email, body)

async def send_invitation_email(email: str, token: str, inviter_name: str = "Administrator"):
    body = f"""
    <h1>Welcome to Team Portal!</h1>
    <p>Hello,</p>
    <p><strong>{inviter_name}</strong> has invited you to join their organization on Team Portal.</p>
    <p>Please use the following token to set your password and complete your registration:</p>
    <p><strong>{token}</strong></p>
    <p>If you did not expect this invitation, you can safely ignore this email.</p>
    """
    await send_email("You've been invited to Team Portal!", email, body)
