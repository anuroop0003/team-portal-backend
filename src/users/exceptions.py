from fastapi import status
from src.exceptions import APIException
from src.users import constants


class UserNotFoundError(APIException):
    """Exception raised when a user is not found within the database scope."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constants.ERR_USER_NOT_FOUND,
        )


class UserAlreadyMemberError(APIException):
    """Exception raised when attempting to add a user who is already a member of the organization."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_USER_ALREADY_MEMBER,
        )


class LastAdminDeletionError(APIException):
    """Exception raised when trying to delete the last administrator of an organization."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_LAST_ADMIN_DELETION,
        )
