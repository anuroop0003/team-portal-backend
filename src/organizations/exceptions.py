from fastapi import status
from src.exceptions import APIException
from src.organizations import constants


class OrganizationNotFoundError(APIException):
    """Exception raised when a requested organization does not exist in the database."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=constants.ERR_ORGANIZATION_NOT_FOUND,
        )


class OrganizationAlreadyExistsError(APIException):
    """Exception raised when trying to create an organization with an already existing code."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ERR_ORGANIZATION_ALREADY_EXISTS,
        )
