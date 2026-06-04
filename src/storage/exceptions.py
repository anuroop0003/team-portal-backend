from fastapi import status
from src.exceptions import APIException
from src.storage import constants


class StorageUploadError(APIException):
    """Exception raised when storage upload fails."""

    def __init__(self, detail: str = constants.ERR_STORAGE_UPLOAD_FAILED):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class StorageDeleteError(APIException):
    """Exception raised when storage deletion fails."""

    def __init__(self, detail: str = constants.ERR_STORAGE_DELETE_FAILED):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class InvalidFileTypeError(APIException):
    """Exception raised when file type is not allowed."""

    def __init__(self, detail: str = constants.ERR_INVALID_FILE_TYPE):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class FileTooLargeError(APIException):
    """Exception raised when file exceeds size limit."""

    def __init__(self, detail: str = constants.ERR_FILE_TOO_LARGE):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class InvalidUploadTypeError(APIException):
    """Exception raised when an invalid upload type prefix is requested."""

    def __init__(self, detail: str = constants.ERR_INVALID_UPLOAD_TYPE):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
