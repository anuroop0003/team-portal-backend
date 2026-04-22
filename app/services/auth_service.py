import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import mailtrap as mt
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.auth_schema import TokenData

# OAuth2 settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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

async def send_email_from_template(template_id: str, recipient: str, variables: dict):
    # If mail settings are missing or default, log instead of failing in dev
    if not settings.MAILTRAP_TOKEN or not template_id:
        print(f"DEBUG EMAIL [Template: {template_id}]: To: {recipient} | Vars: {variables}")
        return

    try:
        mail = mt.MailFromTemplate(
            sender=mt.Address(email=settings.MAIL_FROM, name=settings.COMPANY_NAME),
            to=[mt.Address(email=recipient)],
            template_uuid=template_id,
            template_variables={
                **variables,
                "company_name": settings.COMPANY_NAME,
                "support_email": settings.SUPPORT_EMAIL,
                "user_email": recipient
            }
        )

        client = mt.MailtrapClient(token=settings.MAILTRAP_TOKEN)
        await run_in_threadpool(client.send, mail)
    except Exception as e:
        print(f"ERROR SENDING EMAIL (Mailtrap Template): {e}")

async def send_verification_email(email: str):
    # Create a verification token (valid for 15 minutes)
    token = create_access_token(
        data={"sub": email, "type": "verification"},
        expires_delta=timedelta(minutes=15)
    )
    
    link = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    await send_email_from_template(
        template_id=settings.MAILTRAP_VERIFY_TEMPLATE_ID,
        recipient=email,
        variables={"link": link}
    )

async def send_reset_password_email(email: str, token: str):
    link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    await send_email_from_template(
        template_id=settings.MAILTRAP_RESET_TEMPLATE_ID,
        recipient=email,
        variables={"link": link}
    )

async def send_invitation_email(email: str, inviter_name: str = "Administrator"):
    # Create an invitation token (valid for 24 hours)
    token = create_access_token(
        data={"sub": email, "type": "invitation"},
        expires_delta=timedelta(hours=24)
    )
    
    link = f"{settings.FRONTEND_URL}/auth/onboarding?token={token}"
    
    await send_email_from_template(
        template_id=settings.MAILTRAP_INVITE_TEMPLATE_ID,
        recipient=email,
        variables={
            "inviter_name": inviter_name,
            "link": link
        }
    )
