import aioboto3
from app.core.config import settings
import uuid
import urllib.parse

class StorageService:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.BUCKET_NAME
        self.endpoint_url = settings.BUCKET_ENDPOINT
        self.access_key = settings.BUCKET_ACCESS_KEY_ID
        self.secret_key = settings.BUCKET_SECRET_KEY_ID
        self.region = settings.BUCKET_REGION

    async def upload_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        """
        Uploads a file to Supabase Storage and returns the public URL.
        """
        # Generate a unique path for the file to avoid collisions
        unique_filename = f"{uuid.uuid4()}-{filename}"
        file_path = f"uploads/{unique_filename}"

        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type or "application/octet-stream"
            )
            
            # For Supabase, the public URL pattern is usually:
            # {BUCKET_ENDPOINT}/object/public/{BUCKET_NAME}/{FILE_PATH}
            # Note: BUCKET_ENDPOINT for S3 is usually: https://{project_ref}.storage.supabase.co/storage/v1/s3
            # But the public URL is usually: https://{project_ref}.supabase.co/storage/v1/object/public/{BUCKET_NAME}/{FILE_PATH}
            
            # Let's derive the base URL from the endpoint
            # BUCKET_ENDPOINT: https://clsdsmzslufyndfsberf.storage.supabase.co/storage/v1/s3
            base_url = self.endpoint_url.replace("/s3", "").replace(".storage", "")
            # Modified base_url: https://clsdsmzslufyndfsberf.supabase.co/storage/v1
            
            encoded_bucket = urllib.parse.quote(self.bucket_name)
            public_url = f"{base_url}/object/public/{encoded_bucket}/{file_path}"
            return public_url

storage_service = StorageService()
