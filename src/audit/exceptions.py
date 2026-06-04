from fastapi import status
from src.exceptions import APIException


class AuditLogError(APIException):
    """
    Exception raised when an audit log entry fails to be created in the database.
    """

    def __init__(self, detail: str = "Failed to create audit log"):
        """
        Initializes the AuditLogError exception.

        Args:
            detail (str): Human-readable error message details. Defaults to "Failed to create audit log".
        """

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
