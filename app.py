from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import List
import uuid
from models.document import DocumentResponse, BulkUploadResponse
from models.chunk import SearchResult, DocumentChunk
from models.dataModels import SearchQuery, CollectionStats
from db import get_db_connection, init_db
from repository.vector_pipeline import VectorPipeline
from dotenv import load_dotenv
from repository.sqlDB import create_document_record, get_document_by_id
from models.documentDto import create_document_response
from models.user_models import UserRegistration,AuthResponse, UserResponse
from repository.user_manager import UserManager
from repository.chat_manager import ChatManager
from repository.auth_dependencies import get_current_user, get_current_active_user
#Initialize database and create FastAPI app
app = FastAPI(title="Document Manager API", version="1.0.0")

# Add CORS middleware to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

load_dotenv()
init_db()
user_manager = UserManager()
chat_manager = ChatManager(user_manager=user_manager)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.getenv("UPLOAD_DIR") or "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize vector pipeline
try:
    vector_pipeline = VectorPipeline()
    VECTOR_PIPELINE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Vector pipeline not available: {e}")
    VECTOR_PIPELINE_AVAILABLE = False

def get_supported_content_type(filename: str, original_content_type: str | None) -> str:
    """Determine the content type for a file, prioritizing file extension over MIME type"""
    supported_types = ["text/plain", "text/markdown", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/png", "image/jpeg", "image/gif", "image/bmp", "image/tiff"]
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension == '.txt':
        return "text/plain"
    elif file_extension == '.md':
        return "text/markdown"
    elif file_extension == '.pdf':
        return "application/pdf"
    elif file_extension == '.docx':
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
        if file_extension == '.png':
            return "image/png"
        elif file_extension in ['.jpg', '.jpeg']:
            return "image/jpeg"
        elif file_extension == '.gif':
            return "image/gif"
        elif file_extension == '.bmp':
            return "image/bmp"
        elif file_extension == '.tiff':
            return "image/tiff"
        else:
            return "image/jpeg"  # Default fallback for image files
    else:
        return original_content_type or "application/octet-stream"

def is_vector_processable(content_type: str) -> bool:
    """Check if a content type can be processed by the vector pipeline"""
    return content_type in ["text/plain", "text/markdown", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or content_type.startswith("image/")

def save_uploaded_file(file: UploadFile) -> tuple[str, str, int]:
    """Save an uploaded file and return the unique filename, file path and size"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    return unique_filename, file_path, file_size



def process_single_document(file: UploadFile, description: str | None = None) -> DocumentResponse:
    """Process a single document upload with vector processing"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Determine content type
    content_type = get_supported_content_type(file.filename, file.content_type)
    
    # Save file to disk and get unique filename, file path and size
    unique_filename, file_path, file_size = save_uploaded_file(file)
    
    # Create document record
    document_id = create_document_record(unique_filename, file.filename, file_path, file_size, content_type, description)
    
    # Process through vector pipeline if available and supported
    processing_result = process_document_with_vector_pipeline(file_path, content_type, document_id, file.filename, description)
    
    # Get the created document
    document = get_document_by_id(document_id)
    
    # Create and return response
    return create_document_response(document, processing_result)

def process_document_with_vector_pipeline(file_path: str, content_type: str, document_id: int, 
                                        original_filename: str, description: str | None) -> dict | None:
    """Process a document through the vector pipeline if available and supported"""
    if not VECTOR_PIPELINE_AVAILABLE or not is_vector_processable(content_type):
        return None
    
    try:
        return vector_pipeline.process_document(
            file_path, content_type, document_id, original_filename, description
        )
    except Exception as e:
        print(f"Warning: Vector processing failed for document {document_id}: {e}")
        return None


@app.post("/api/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: str | None = None
):
    """Upload a new document"""
    return process_single_document(file, description)

@app.post("/api/documents/upload-multiple", response_model=BulkUploadResponse)
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    description: str | None = None
):
    """Upload multiple documents at once"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Limit to 10 files per request
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request")
    
    uploaded_documents = []
    errors = []
    
    for file in files:
        try:
            if not file.filename:
                errors.append(f"File {file.filename or 'unnamed'}: No filename provided")
                continue
            
            # Process the document using the reusable function
            doc_response = process_single_document(file, description)
            uploaded_documents.append(doc_response)
            
        except Exception as e:
            errors.append(f"File {file.filename}: {str(e)}")
            # Note: Cleanup is handled within process_single_document function
    
    return BulkUploadResponse(
        message=f"Upload completed. {len(uploaded_documents)} files uploaded successfully.",
        uploaded_count=len(uploaded_documents),
        documents=uploaded_documents,
        errors=errors
    )

@app.get("/api/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get all documents"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents ORDER BY upload_date DESC')
    documents = cursor.fetchall()
    conn.close()
    
    return [
        DocumentResponse(
            id=doc['id'],
            filename=doc['filename'],
            original_filename=doc['original_filename'],
            file_path=doc['file_path'],
            file_size=doc['file_size'],
            content_type=doc['content_type'],
            upload_date=doc['upload_date'],
            description=doc['description']
        )
        for doc in documents
    ]

@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int):
    """Get a specific document by ID"""
    document = get_document_by_id(document_id)
    
    return DocumentResponse(
        id=document['id'],
        filename=document['filename'],
        original_filename=document['original_filename'],
        file_path=document['file_path'],
        file_size=document['file_size'],
        content_type=document['content_type'],
        upload_date=document['upload_date'],
        description=document['description']
    )

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int):
    """Delete a document by ID"""
    document = get_document_by_id(document_id)
    
    # Delete from vector database if available
    if VECTOR_PIPELINE_AVAILABLE:
        try:
            vector_pipeline.delete_document_chunks(document_id)
        except Exception as e:
            print(f"Warning: Failed to delete vector chunks for document {document_id}: {e}")
    
    # Delete file from disk
    if os.path.exists(document['file_path']):
        os.remove(document['file_path'])
    
    # Delete from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Document deleted successfully"}

# Vector pipeline endpoints
@app.post("/api/search", response_model=List[SearchResult])
async def search_documents(query: SearchQuery):
    """Search documents by semantic similarity"""
    if not VECTOR_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vector pipeline not available")
    
    try:
        results = vector_pipeline.search_documents(query.query, query.n_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/documents/{document_id}/chunks", response_model=List[DocumentChunk])
async def get_document_chunks(document_id: int):
    """Get all chunks for a specific document"""
    if not VECTOR_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vector pipeline not available")
    
    try:
        chunks = vector_pipeline.get_document_chunks(document_id)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunks: {str(e)}")

@app.get("/api/vector/stats", response_model=CollectionStats)
async def get_vector_stats():
    """Get statistics about the vector collection"""
    if not VECTOR_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vector pipeline not available")
    
    try:
        stats = vector_pipeline.get_collection_stats()
        return CollectionStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/api/documents/{document_id}/reprocess")
async def reprocess_document(document_id: int):
    """Reprocess a document through the vector pipeline"""
    if not VECTOR_PIPELINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Vector pipeline not available")
    
    # Get document info
    document = get_document_by_id(document_id)
    
    # Check if file type is supported
    supported_types = ["text/plain", "text/markdown"]
    if document['content_type'] not in supported_types:
        raise HTTPException(status_code=400, detail="Document type not supported for vector processing")
    
    try:
        # Delete existing chunks
        vector_pipeline.delete_document_chunks(document_id)
        
        # Reprocess document
        result = vector_pipeline.process_document(
            document['file_path'],
            document['content_type'],
            document_id,
            document['original_filename'],
            document['description']
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")
    
@app.post("/api/auth/register")
async def register_user(user: UserRegistration):
    """Register a new user"""
    try:
        res = user_manager.create_user(user.username, user.email, user.password)
        if res['error']:
            raise HTTPException(status_code=400, detail=res['error'])
        return {"message": "User registered successfully", "user_id": res['user_id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
        

@app.post("/api/auth/login")
async def login_user(user: UserRegistration):
    """User login"""
    try: 
        res = user_manager.authenticate_user(user.username, user.password)
        if res['error'] and res['status_code'] == 401:
            raise HTTPException(status_code=401, detail=res['error'])
        if res['error']:
            raise HTTPException(status_code=500, detail=res['error'])
        return AuthResponse(
            success=True,
            user=res['user'],
            session_token=res['session_token'],
            expires_at=res['expires_at'],
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
@app.get("/api/auth/profile", response_model=UserResponse)
async def get_user_profile(session_token: str):
    """Get user profile information"""
    try:
        res = user_manager.validate_session(session_token)
        if not res:
            raise HTTPException(status_code=401, detail="Invalid session token")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    endpoints = {
        "upload_single": "POST /api/documents/upload",
        "upload_multiple": "POST /api/documents/upload-multiple",
        "list": "GET /api/documents",
        "get": "GET /api/documents/{id}",
        "delete": "DELETE /api/documents/{id}"
    }
    
    # Add vector pipeline endpoints if available
    if VECTOR_PIPELINE_AVAILABLE:
        endpoints.update({
            "search": "POST /api/search",
            "chunks": "GET /api/documents/{id}/chunks",
            "vector_stats": "GET /api/vector/stats",
            "reprocess": "POST /api/documents/{id}/reprocess"
        })
    
    return {
        "message": "Document Manager API",
        "version": "1.0.0",
        "vector_pipeline": VECTOR_PIPELINE_AVAILABLE,
        "endpoints": endpoints
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
