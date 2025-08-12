from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from datetime import datetime
import os
import shutil
from typing import List
import uuid
import json
from models import DocumentResponse, DocumentUpload
from db import get_db_connection, init_db
from dotenv import load_dotenv

#Initialize database and create FastAPI app
app = FastAPI(title="Document Manager API", version="1.0.0")
load_dotenv()
init_db()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.getenv("UPLOAD_DIR") or "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: str | None = None
):
    """Upload a new document"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create document record
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO documents (filename, original_filename, file_path, file_size, content_type, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (unique_filename, file.filename, file_path, file_size, file.content_type or "application/octet-stream", description))
    
    document_id = cursor.lastrowid
    conn.commit()
    
    # Get the created document
    cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
    document = cursor.fetchone()
    conn.close()
    
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
    document = cursor.fetchone()
    conn.close()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get document info before deletion
    cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
    document = cursor.fetchone()
    
    if not document:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    if os.path.exists(document['file_path']):
        os.remove(document['file_path'])
    
    # Delete from database
    cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Document deleted successfully"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Manager API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/documents/upload",
            "list": "GET /api/documents",
            "get": "GET /api/documents/{id}",
            "delete": "DELETE /api/documents/{id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
