from fastapi import status
from src.exceptions import APIException
from src.auth import constants


class EmailAlreadyRegisteredError(APIException):
    """Exception raised when registering an email that already exists in the system."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_EMAIL_ALREADY_REGISTERED,
        )


class RegistrationFailedError(APIException):
    """Exception raised when an organization/user registration transaction fails."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{constants.ERR_REGISTRATION_FAILED_PREFIX}: {message}",
        )


class AuthenticationError(APIException):
    """Exception raised when user authentication fails due to invalid credentials."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=constants.ERR_MSG_INVALID_CREDENTIALS,
            error_code=constants.ERR_CODE_INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AccountDeactivatedError(APIException):
    """Exception raised when trying to log into a deactivated user account."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_MSG_ACCOUNT_DEACTIVATED,
            error_code=constants.ERR_CODE_ACCOUNT_DEACTIVATED,
        )


class EmailNotVerifiedError(APIException):
    """Exception raised when a user tries to sign in but has not verified their email."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=constants.ERR_MSG_EMAIL_NOT_VERIFIED,
            error_code=constants.ERR_CODE_EMAIL_NOT_VERIFIED,
        )


class InvalidTokenError(APIException):
    """Exception raised when a JWT token cannot be parsed or validated."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_INVALID_TOKEN,
        )


class InvalidOrExpiredVerificationTokenError(APIException):
    """Exception raised when an email verification link token is invalid or expired."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_INVALID_EXPIRED_VERIFICATION_TOKEN,
        )


class InvalidOrExpiredResetTokenError(APIException):
    """Exception raised when a password reset token is invalid or expired."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_INVALID_EXPIRED_RESET_TOKEN,
        )


class UserNotFoundError(APIException):
    """Exception raised when the requested user is not found in the database."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_USER_NOT_FOUND,
        )
