from datetime import datetime, timedelta
from typing import Optional
import jwt
from src.config import settings
import uuid
import logging
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError
from src.users import service as user_service
from src.organizations import service as organization_service
from src.users.schemas import CreateUser
from src.auth.utils import verify_password, hash_password, create_access_token
from src.auth import constants
from src.auth import exceptions as auth_exceptions
from src.exceptions import APIException


async def send_verification_email(email: str):
    """
    Generates a verification link containing a JWT verification token.

    Args:
        email (str): The email address to verify.

    Returns:
        str: The fully-qualified verification URL.
    """

    token = create_access_token(
        data={"sub": email, "type": constants.TOKEN_TYPE_VERIFICATION},
        expires_delta=timedelta(minutes=constants.VERIFICATION_TOKEN_EXPIRE_MINUTES),
    )

    return f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"


async def send_reset_password_email(email: str, token: str):
    """
    Generates a password reset URL using a reset token.

    Args:
        email (str): The recipient user's email.
        token (str): The reset token UUID string.

    Returns:
        str: The password reset URL.
    """

    return f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"


async def send_invitation_email(
    email: str, inviter_name: str = constants.DEFAULT_INVITER_NAME
):
    """
    Generates an invitation link for user onboarding.

    Args:
        email (str): The email address of the invited user.
        inviter_name (str, optional): The name of the inviting entity/user. Defaults to DEFAULT_INVITER_NAME.

    Returns:
        str: The onboarding URL.
    """

    token = create_access_token(
        data={"sub": email, "type": constants.TOKEN_TYPE_INVITATION},
        expires_delta=timedelta(hours=constants.INVITATION_TOKEN_EXPIRE_HOURS),
    )

    return f"{settings.FRONTEND_URL}/auth/onboarding?token={token}"


async def register_organization_workflow(
    db: Session, payload, ip_address: Optional[str]
):
    """
    Executes the organization registration transaction, including owner and membership creation.

    Args:
        db (Session): The database session.
        payload: Pydantic registration payload containing admin and organization details.
        ip_address (Optional[str]): The client's IP address.

    Returns:
        User: The newly registered owner User database model.

    Raises:
        EmailAlreadyRegisteredError: If the admin's email is already registered.
        RegistrationFailedError: If database transaction fails.
    """

    if user_service.get_user_by_email(db, payload.admin.email):
        raise auth_exceptions.EmailAlreadyRegisteredError()

    try:
        org = organization_service.create_organization(db, payload.organization)

        user = await user_service.create_user(
            db,
            CreateUser(
                name=payload.admin.name,
                email=payload.admin.email,
                password=payload.admin.password,
                phone=payload.admin.phone,
                designation=payload.admin.job_title,
                organization_id=org.id,
            ),
            role=constants.ROLE_OWNER,
            ip_address=ip_address,
        )

        db.commit()
        db.refresh(user)

        # Generate verification link
        link = await send_verification_email(user.email)

        user.verification_link = link

        return user

    except APIException:
        db.rollback()
        raise

    except Exception as e:
        logging.error(e)
        db.rollback()
        raise auth_exceptions.RegistrationFailedError(str(e))


def authenticate_user(db: Session, credentials, ip_address: Optional[str]):
    """
    Authenticates a user's sign-in credentials.

    Args:
        db (Session): The database session.
        credentials: The sign-in payload with email and password.
        ip_address (Optional[str]): The client's IP address.

    Returns:
        tuple[dict, User]: A tuple containing the access token payload and the User object.

    Raises:
        AuthenticationError: If email/password matches nothing or is incorrect.
        AccountDeactivatedError: If the account is deactivated.
        EmailNotVerifiedError: If the user's email has not been verified.
    """

    user = user_service.get_user_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise auth_exceptions.AuthenticationError()

    if not user.is_active:
        raise auth_exceptions.AccountDeactivatedError()

    if not user.is_verified:
        raise auth_exceptions.EmailNotVerifiedError()

    token = create_access_token(data={"sub": user.email, "id": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}, user


def verify_email_workflow(db: Session, token: str):
    """
    Verifies a user's email matching the provided token.

    Args:
        db (Session): The database session.
        token (str): The verification JWT.

    Returns:
        dict: A success status message.

    Raises:
        InvalidTokenError: If the token structure is invalid.
        InvalidOrExpiredVerificationTokenError: If the token signature is invalid or expired.
        UserNotFoundError: If the user encoded in the token doesn't exist.
    """

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")

        if email is None or payload.get("type") != constants.TOKEN_TYPE_VERIFICATION:
            raise auth_exceptions.InvalidTokenError()

    except InvalidTokenError:
        raise auth_exceptions.InvalidOrExpiredVerificationTokenError()

    user = user_service.get_user_by_email(db, email)

    if not user:
        raise auth_exceptions.UserNotFoundError()

    user.is_verified = True

    db.commit()

    return {"message": constants.MSG_EMAIL_VERIFIED_SUCCESS}


def verify_token_info_workflow(db: Session, token: str):
    """
    Validates a token and returns user detail info.

    Args:
        db (Session): The database session.
        token (str): The verification JWT.

    Returns:
        dict: Containing email and token validity.

    Raises:
        InvalidTokenError: If token structure is invalid.
        InvalidOrExpiredVerificationTokenError: If token is expired.
        UserNotFoundError: If user is not found.
    """

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")

        if email is None or payload.get("type") != constants.TOKEN_TYPE_VERIFICATION:
            raise auth_exceptions.InvalidTokenError()

    except InvalidTokenError:
        raise auth_exceptions.InvalidOrExpiredVerificationTokenError()

    user = user_service.get_user_by_email(db, email)

    if not user:
        raise auth_exceptions.UserNotFoundError()

    return {"email": user.email, "is_valid": True}


async def send_verification_workflow(db: Session, email: str):
    """
    Initiates resending verification link to a user.

    Args:
        db (Session): The database session.
        email (str): The email address of the user.

    Returns:
        dict: Status message along with the newly generated link.
    """

    user = user_service.get_user_by_email(db, email)

    if not user:
        return {"message": constants.MSG_VERIFICATION_SENT_FALLBACK}

    if user.is_verified:
        return {"message": constants.MSG_EMAIL_ALREADY_VERIFIED}

    link = await send_verification_email(user.email)

    return {"message": constants.MSG_VERIFICATION_LINK_GENERATED, "link": link}


async def forgot_password_workflow(db: Session, email: str):
    """
    Initiates forgot password workflow and generates a reset token link.

    Args:
        db (Session): The database session.
        email (str): The user's registered email address.

    Returns:
        dict: Status message along with the reset link.
    """

    user = user_service.get_user_by_email(db, email)

    if user:
        user.reset_token = str(uuid.uuid4())

        db.commit()

        link = await send_reset_password_email(user.email, user.reset_token)

        return {"message": constants.MSG_RESET_LINK_GENERATED, "link": link}

    return {"message": constants.MSG_RESET_SENT_FALLBACK}


def reset_password_workflow(
    db: Session, token: str, new_password: str, ip_address: Optional[str]
):
    """
    Resets the user's password utilizing the password reset token.

    Args:
        db (Session): The database session.
        token (str): The password reset token UUID string.
        new_password (str): The new plain-text password to apply.
        ip_address (Optional[str]): The client's IP address.

    Returns:
        tuple[dict, User]: Success payload status message and the User database model.

    Raises:
        InvalidOrExpiredResetTokenError: If the token is invalid or expired.
    """

    user = user_service.get_user_by_reset_token(db, token)

    if not user:
        raise auth_exceptions.InvalidOrExpiredResetTokenError()

    user.hashed_password = hash_password(new_password)

    user.reset_token = None

    db.commit()

    return {"message": constants.MSG_PASSWORD_RESET_SUCCESS}, user


async def invite_user_workflow(
    db: Session, user_data, role: str = "EMPLOYEE", ip_address: Optional[str] = None
):
    """
    Invites a new user to join the organization, generating an invitation link if no password is set.

    Args:
        db (Session): The database session.
        user_data: Pydantic payload representing the user's creation data.
        role (str, optional): Role designation. Defaults to "EMPLOYEE".
        ip_address (Optional[str], optional): The client's IP address. Defaults to None.

    Returns:
        User: The newly created User database model.
    """

    user = await user_service.create_user(
        db, user_data, role=role, ip_address=ip_address
    )

    if not user_data.password:
        link = await send_invitation_email(user.email)

        user.invitation_link = link

    return user
