from fastapi import Request
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.users.models import User
from src.auth.schemas import (
    SignInRequest,
    Token,
    OrganizationRegisterRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthMeResponse,
    SendVerificationRequest,
    VerifyTokenInfoResponse,
)
from src.auth import service as auth_service
from src.auth import constants
from src.auth.dependencies import get_current_active_user
from src.audit.dependencies import audit_logger, set_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-organization", response_model=AuthMeResponse)
async def register_organization(
    request: Request,
    payload: OrganizationRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new organization and create the initial owner account.

    Args:
        request (Request): The incoming request to extract client IP.
        payload (OrganizationRegisterRequest): Details of the organization and owner.
        db (Session): The database session dependency.

    Returns:
        AuthMeResponse: User details of the newly created owner.
    """

    return await auth_service.register_organization_workflow(
        db, payload, ip_address=request.client.host
    )


@router.post("/sign-in", response_model=Token, dependencies=[Depends(audit_logger)])
def sign_in(
    request: Request, credentials: SignInRequest, db: Session = Depends(get_db)
):
    """
    Authenticate user credentials and return an access token.

    Args:
        request (Request): The incoming request to extract client IP and set audit event.
        credentials (SignInRequest): The user's email and password.
        db (Session): The database session dependency.

    Returns:
        Token: The JWT access token and token type.
    """

    res, user = auth_service.authenticate_user(
        db, credentials, ip_address=request.client.host
    )

    set_audit_event(
        request,
        user.organization_id,
        constants.AUDIT_SIGN_IN,
        target_id=user.id,
        actor_id=user.id,
    )

    return res


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify a user's email address using a verification token.

    Args:
        token (str): The verification JWT token.
        db (Session): The database session dependency.

    Returns:
        dict: A success message.
    """
    return auth_service.verify_email_workflow(db, token)


@router.get("/verify-token-info", response_model=VerifyTokenInfoResponse)
def verify_token_info(token: str, db: Session = Depends(get_db)):
    """
    Decode a verification token and return validation info.

    Args:
        token (str): The verification JWT token.
        db (Session): The database session dependency.

    Returns:
        VerifyTokenInfoResponse: Decoded validation info.
    """

    return auth_service.verify_token_info_workflow(db, token)


@router.post("/send-verification")
async def send_verification(
    payload: SendVerificationRequest, db: Session = Depends(get_db)
):
    """
    Resend the email verification link to a user.

    Args:
        payload (SendVerificationRequest): Email to resend verification link for.
        db (Session): The database session dependency.

    Returns:
        dict: A success or status message.
    """

    return await auth_service.send_verification_workflow(db, payload.email)


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    """
    Generate a password reset link and send it via email.

    Args:
        payload (ForgotPasswordRequest): Email of the user who forgot their password.
        db (Session): The database session dependency.

    Returns:
        dict: A status message containing the reset link.
    """

    return await auth_service.forgot_password_workflow(db, payload.email)


@router.post("/reset-password", dependencies=[Depends(audit_logger)])
def reset_password(
    request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """
    Reset the user's password using a reset token.

    Args:
        request (Request): The incoming request for auditing and IP context.
        payload (ResetPasswordRequest): The reset token and new password.
        db (Session): The database session dependency.

    Returns:
        dict: A success message.
    """

    res, user = auth_service.reset_password_workflow(
        db, payload.token, payload.new_password, ip_address=request.client.host
    )

    set_audit_event(
        request,
        user.organization_id,
        constants.AUDIT_RESET_PASSWORD,
        target_id=user.id,
        actor_id=user.id,
    )

    return res


@router.get("/me", response_model=AuthMeResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the profile details of the current authenticated user.

    Args:
        current_user (User): The authenticated active User.

    Returns:
        AuthMeResponse: User details.
    """

    return current_user
