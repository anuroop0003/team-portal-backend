from pydantic import BaseModel


class UploadResponse(BaseModel):
    """
    Schema for storage upload response details.
    """

    url: str
    filename: str
    status: str
