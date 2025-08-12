from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ProcessingResult(BaseModel):
    document_id: int
    original_filename: str
    total_chunks: int
    total_tokens: int
    chunk_ids: List[str]
    status: str
    error: Optional[str] = None

class SearchQuery(BaseModel):
    query: str
    n_results: int = 5

class CollectionStats(BaseModel):
    total_chunks: int
    collection_name: str
    sample_metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None