import boto3
import uuid
import asyncio
import logging
import urllib.parse
from botocore.exceptions import ClientError
from src.config import settings
from src.storage.constants import (
    ALLOWED_IMAGE_TYPES,
    MAX_FILE_SIZE,
    DEFAULT_CONTENT_TYPE,
)
from src.storage.exceptions import (
    StorageUploadError,
    StorageDeleteError,
    InvalidFileTypeError,
    FileTooLargeError,
)

logger = logging.getLogger(__name__)


class StorageService:
    """
    Service for handling interactions with S3/Supabase Storage.
    """

    def __init__(self):
        self.bucket_name = settings.BUCKET_NAME
        self.endpoint_url = settings.BUCKET_ENDPOINT
        self.access_key = settings.BUCKET_ACCESS_KEY_ID
        self.secret_key = settings.BUCKET_SECRET_KEY_ID
        self.region = settings.BUCKET_REGION

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        upload_type: str = "uploads",
        content_type: str = None,
    ) -> str:
        """
        Uploads a general file to storage and returns the public URL.

        Args:
            file_content (bytes): The raw bytes of the file.
            filename (str): The original filename.
            upload_type (str, optional): The directory prefix for storage grouping. Defaults to "uploads".
            content_type (str, optional): The MIME type of the file. Defaults to None.

        Returns:
            str: The public URL of the uploaded file.

        Raises:
            StorageUploadError: If the upload operation fails.
        """

        if upload_type == "profile":
            if content_type not in ALLOWED_IMAGE_TYPES:
                raise InvalidFileTypeError()
            if len(file_content) > MAX_FILE_SIZE:
                raise FileTooLargeError()

        unique_filename = f"{uuid.uuid4()}-{filename}"
        file_path = f"{upload_type}/{unique_filename}"
        content_type = content_type or DEFAULT_CONTENT_TYPE

        try:
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type,
            )

            # Derive the base URL from the endpoint
            base_url = self.endpoint_url.replace("/s3", "").replace(".storage", "")
            encoded_bucket = urllib.parse.quote(self.bucket_name)
            public_url = f"{base_url}/object/public/{encoded_bucket}/{file_path}"
            return public_url

        except Exception as e:
            logger.exception("General file upload failed")
            raise StorageUploadError(detail=f"Failed to upload file: {str(e)}")

    async def delete_file(self, object_key: str) -> None:
        """
        Deletes a file from storage.

        Args:
            object_key (str): The S3 key/path of the object to delete.

        Returns:
            None

        Raises:
            StorageDeleteError: If the delete operation fails.
        """
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=object_key,
            )
        except ClientError as e:
            logger.exception("File deletion failed")
            raise StorageDeleteError(detail=f"Failed to delete file: {str(e)}")


storage_service = StorageService()
