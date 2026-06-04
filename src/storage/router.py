from fastapi import APIRouter, Depends, UploadFile, File
from src.storage.service import storage_service
from src.storage.schemas import UploadResponse
from src.auth.dependencies import get_current_active_user
from src.users.models import User
from src.storage.constants import (
    ALLOWED_IMAGE_TYPES,
    MAX_FILE_SIZE,
    ALLOWED_UPLOAD_TYPES,
)
from src.storage.exceptions import (
    InvalidFileTypeError,
    FileTooLargeError,
    InvalidUploadTypeError,
)

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post(
    "/upload", response_model=UploadResponse, summary="Upload a file to storage"
)
async def upload_file(
    file: UploadFile = File(...),
    upload_type: str = "profile",
    current_user: User = Depends(get_current_active_user),
) -> UploadResponse:
    """
    Uploads a file to Storage and returns the public URL.

    Args:
        file (UploadFile): The file to upload.
        upload_type (str, optional): The directory prefix for storage grouping. Defaults to "profile".
        current_user (User): The authenticated active user making the request.

    Returns:
        UploadResponse: The URL and metadata of the uploaded file.
    """
    if upload_type not in ALLOWED_UPLOAD_TYPES:
        raise InvalidUploadTypeError()

    content = await file.read()
    filename = file.filename
    content_type = file.content_type

    url = await storage_service.upload_file(
        file_content=content,
        filename=filename,
        upload_type=upload_type,
        content_type=content_type,
    )

    return UploadResponse(url=url, filename=filename, status="success")


@router.post(
    "/upload-public",
    response_model=UploadResponse,
    summary="Upload a file to storage publicly",
)
async def upload_file_public(
    file: UploadFile = File(...),
    upload_type: str = "logo",
) -> UploadResponse:
    """
    Uploads an image file to Storage publicly (without authentication) and returns the public URL.
    Meant for organization logos during registration.
    """
    if upload_type not in ALLOWED_UPLOAD_TYPES:
        raise InvalidUploadTypeError()

    content = await file.read()
    filename = file.filename
    content_type = file.content_type

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise InvalidFileTypeError()
    if len(content) > MAX_FILE_SIZE:
        raise FileTooLargeError()

    url = await storage_service.upload_file(
        file_content=content,
        filename=filename,
        upload_type=upload_type,
        content_type=content_type,
    )

    return UploadResponse(url=url, filename=filename, status="success")


@router.delete("/delete", summary="Delete a file from storage")
async def delete_file(
    object_key: str,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Deletes a file from Storage.

    Args:
        object_key (str): The storage key of the file to delete.
        current_user (User): The authenticated active user making the request.

    Returns:
        dict: A status dictionary indicating success.
    """
    await storage_service.delete_file(object_key)

    return {"status": "success", "message": "File deleted successfully"}
