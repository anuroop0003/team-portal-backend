# Local constants for storage integration
DEFAULT_CONTENT_TYPE = "application/octet-stream"

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

# Error Message Constants
ERR_STORAGE_UPLOAD_FAILED = "Failed to upload file to storage."
ERR_STORAGE_DELETE_FAILED = "Failed to delete file from storage."
ERR_INVALID_FILE_TYPE = "Only JPEG, PNG, and WebP images are allowed."
ERR_FILE_TOO_LARGE = "File size must be less than 2 MB."
