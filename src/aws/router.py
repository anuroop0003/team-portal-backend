from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.aws.client import storage_service
from src.auth.dependencies import get_current_active_user
from src.users.models import User

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post("/upload", summary="Upload a file to storage")
async def upload_file(
    file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)
):
    """
    Uploads a file to Supabase Storage and returns the public URL.
    Requires authentication.
    """
    try:
        content = await file.read()
        filename = file.filename
        content_type = file.content_type

        url = await storage_service.upload_file(
            file_content=content, filename=filename, content_type=content_type
        )

        return {"url": url, "filename": filename, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
