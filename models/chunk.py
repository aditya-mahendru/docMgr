from pydantic import BaseModel
from typing import Optional

class ChunkMetadata(BaseModel):
    document_id: int
    chunk_index: int
    original_filename: str
    content_type: str
    description: Optional[str] = None
    chunk_size: int
    total_chunks: int

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    
class SearchResult(BaseModel):
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    similarity_score: float