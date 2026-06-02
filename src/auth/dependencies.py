import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from src.config import settings
from src.database import get_db
from src.users.models import User
from src.auth.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/sign-in")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Decodes the JWT token to retrieve and return the authenticated user.

    Args:
        token (str): The bearer token provided in the authorization header.
        db (Session): The database session dependency.

    Returns:
        User: The authenticated User object.

    Raises:
        HTTPException: If the token is invalid, expired, or the user does not exist.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")
        user_id: str = payload.get("id")

        if email is None or user_id is None:
            raise credentials_exception

        token_data = TokenData(email=email, user_id=uuid.UUID(user_id))

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Ensures that the authenticated user is currently active.

    Args:
        current_user (User): The authenticated User object from get_current_user.

    Returns:
        User: The active User object.

    Raises:
        HTTPException: If the user is inactive.
    """

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
