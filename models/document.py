from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_date: str
    description: str | None = None
    processing_result: Optional[Dict[str, Any]] = None

class DocumentUpload(BaseModel):
    description: str | None = None
    
    
class BulkUploadResponse(BaseModel):
    message: str
    uploaded_count: int
    documents: List[DocumentResponse]
    errors: List[str] = []