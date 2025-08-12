from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_date: str
    description: str | None = None

class DocumentUpload(BaseModel):
    description: str | None = None