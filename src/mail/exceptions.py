from fastapi import status
from src.exceptions import APIException


class MailSendError(APIException):
    """
    Exception raised when SMTP fails to send an email.
    """

    def __init__(self, detail: str = "Failed to send email"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
