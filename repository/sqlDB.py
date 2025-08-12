from fastapi import HTTPException
from db import get_db_connection

def create_document_record(filename: str, original_filename: str, file_path: str, 
                          file_size: int, content_type: str, description: str | None) -> int:
    """Create a document record in the database and return the document ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO documents (filename, original_filename, file_path, file_size, content_type, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, original_filename, file_path, file_size, content_type, description))
        
        document_id = cursor.lastrowid
        if document_id is None:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        
        conn.commit()
        return document_id
        
    finally:
        conn.close()

def get_document_by_id(document_id: int) -> dict:
    """Retrieve a document from the database by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
        document = cursor.fetchone()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    finally:
        conn.close()