from models.document import DocumentResponse

def create_document_response(document: dict, processing_result: dict | None = None) -> DocumentResponse:
    """Create a DocumentResponse object from a database document and optional processing result"""
    response = DocumentResponse(
        id=document['id'],
        filename=document['filename'],
        original_filename=document['original_filename'],
        file_path=document['file_path'],
        file_size=document['file_size'],
        content_type=document['content_type'],
        upload_date=document['upload_date'],
        description=document['description']
    )
    
    if processing_result:
        response.processing_result = processing_result
    
    return response
