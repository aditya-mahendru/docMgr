# Document Manager API

A FastAPI-based document management system with SQLite backend that supports file upload, retrieval, listing, deletion, and **intelligent vector-based semantic search**.

## Features

- **File Upload**: Upload single documents with optional descriptions
- **Multiple File Upload**: Upload multiple documents at once (up to 10 files)
- **Document Listing**: Get all uploaded documents
- **Document Retrieval**: Get specific document details by ID
- **Document Deletion**: Remove documents from the system
- **Vector Pipeline**: Intelligent document processing with semantic search
- **Text Chunking**: Automatic document segmentation for optimal processing
- **Semantic Search**: Find documents by meaning, not just keywords
- **Image Processing**: OCR extraction and AI-powered description generation
- **SQLite Database**: Local database storage for document metadata
- **ChromaDB Vector Store**: High-performance vector database for embeddings
- **File Storage**: Secure file storage with unique filenames
- **RESTful API**: Clean, REST-compliant endpoints

## Vector Pipeline Features

The system now includes a sophisticated vector pipeline that:

- **Chunks Documents**: Breaks down text into optimal-sized chunks (500 tokens with 50 token overlap)
- **Generates Embeddings**: Uses local sentence-transformers to create semantic vector representations
- **Enables Semantic Search**: Find documents by meaning and context, not just exact text matches
- **Supports Multiple Formats**: Currently supports `.txt`, `.md`, `.pdf`, and `.docx` files
- **Scalable Architecture**: Built with ChromaDB for efficient vector storage and retrieval

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `POST` | `/api/documents/upload` | Upload a single document |
| `POST` | `/api/documents/upload-multiple` | Upload multiple documents (up to 10) |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document details by ID |
| `DELETE` | `/api/documents/{id}` | Delete document by ID |
| `POST` | `/api/search` | **NEW**: Semantic search across documents |
| `GET` | `/api/documents/{id}/chunks` | **NEW**: Get document chunks and embeddings |
| `GET` | `/api/vector/stats` | **NEW**: Get vector collection statistics |
| `POST` | `/api/documents/{id}/reprocess` | **NEW**: Reprocess document through vector pipeline |

## Setup

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- **Tesseract OCR** installed on your system (for image processing)
- **Groq API key** (for AI-powered image description generation)
- **No external API keys required for text processing** (using local sentence-transformers)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd docMgr
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env to add your Groq API key for image processing
   # GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Install Tesseract OCR (required for image processing):**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from https://github.com/UB-Mannheim/tesseract/wiki
   
   # Or use the automated setup script:
   python setup_image_processing.py
   ```

## Usage

### Starting the Server

1. **Activate your virtual environment** (if not already active):
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Run the FastAPI application:**
   ```bash
   python app.py
   ```

   Or alternatively:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API will be available at: http://localhost:8000
   - Interactive API docs (Swagger UI): http://localhost:8000/docs
   - Alternative API docs (ReDoc): http://localhost:8000/redoc

### Testing the API

1. **Run the basic test script:**
   ```bash
   python test_api.py
   ```

2. **Test multiple document upload:**
   ```bash
   python test_multiple_upload.py
   ```

3. **Test vector pipeline functionality:**
   ```bash
   python test_vector_pipeline.py
   ```

4. **Test image processing setup:**
   ```bash
   python test_image_processing.py
   ```

5. **Test image upload and processing:**
   ```bash
   python test_image_upload.py
   ```

4. **Manual testing with curl:**
   ```bash
   # Get API info
   curl http://localhost:8000/
   
   # Upload a single document
   curl -X POST "http://localhost:8000/api/documents/upload" \
        -F "file=@/path/to/your/document.pdf" \
        -F "description=My important document"
   
   # Upload multiple documents
   curl -X POST "http://localhost:8000/api/documents/upload-multiple" \
        -F "files=@/path/to/document1.pdf" \
        -F "files=@/path/to/document2.docx" \
        -F "files=@/path/to/document3.md" \
        -F "description=Bulk upload of multiple documents"
   
   # Upload an image for OCR processing
   curl -X POST "http://localhost:8000/api/documents/upload" \
        -F "file=@/path/to/your/image.jpg" \
        -F "description=Receipt for expense tracking"
   
   # Semantic search
   curl -X POST "http://localhost:8000/api/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is machine learning?", "n_results": 5}'
   
   # Get document chunks
   curl http://localhost:8000/api/documents/1/chunks
   
   # Get vector statistics
   curl http://localhost:8000/api/vector/stats
   
   # List all documents
   curl http://localhost:8000/api/documents
   
   # Get specific document
   curl http://localhost:8000/api/documents/1
   
   # Delete document
   curl -X DELETE http://localhost:8000/api/documents/1
   ```

## Vector Pipeline Architecture

### Document Processing Flow

1. **File Upload**: Document is uploaded and stored
2. **Text Extraction**: Text content is extracted from supported file types
   - **Text/PDF/DOCX**: Direct text extraction
   - **Images**: OCR processing + AI-powered description generation via Groq API
3. **Chunking**: Text is split into optimal-sized chunks using LangChain
4. **Embedding Generation**: Each chunk is converted to a vector using local sentence-transformers
5. **Vector Storage**: Embeddings are stored in ChromaDB with metadata
6. **Search Index**: Vector database enables semantic similarity search

### Image Processing Pipeline

For image files, the system uses a sophisticated processing pipeline:

1. **Image Preprocessing**: OpenCV-based enhancement (denoising, contrast adjustment)
2. **OCR Extraction**: Tesseract OCR for text extraction with multiple PSM modes
3. **AI Analysis**: Groq API integration for intelligent document analysis and description
4. **Content Combination**: OCR text + AI description for comprehensive search indexing
5. **Vector Processing**: Combined content is chunked and embedded like text documents

### Supported File Types

- **Text Files** (`.txt`): Plain text documents
- **Markdown Files** (`.md`): Markdown-formatted documents
- **PDF Files** (`.pdf`): Portable Document Format files with text extraction
- **Word Documents** (`.docx`): Microsoft Word files with structured content extraction
- **Image Files** (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`): OCR processing with AI-powered description generation
- **Future Support**: PowerPoint presentations, Excel spreadsheets, and other formats

### Chunking Strategy

- **Chunk Size**: 500 tokens per chunk
- **Overlap**: 50 tokens between chunks for context preservation
- **Separators**: Intelligent splitting on paragraphs, sentences, and words
- **Token Counting**: Uses tiktoken for accurate token measurement

## Database Schema

The application uses SQLite with the following table structure:

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

### Vector Database (ChromaDB)

- **Collection**: "documents" with cosine similarity
- **Metadata**: Document ID, chunk index, filename, content type, description
- **Embeddings**: 1536-dimensional vectors (text-embedding-ada-002 model)
- **Storage**: Persistent local storage in `./chroma_db/`

## File Storage

- Files are stored in the `uploads/` directory
- Unique filenames are generated using UUID to prevent conflicts
- Original filenames are preserved in the database
- File paths are stored relative to the application root

## Multiple Document Upload

The API supports uploading multiple documents simultaneously:

- **Endpoint**: `POST /api/documents/upload-multiple`
- **File Limit**: Maximum 10 files per request
- **Response**: Includes count of successful uploads and any error details
- **Error Handling**: Individual file failures don't prevent other files from uploading
- **Transaction Safety**: Each file is processed independently with proper cleanup on failure

**Response Format:**
```json
{
  "message": "Upload completed. 3 files uploaded successfully.",
  "uploaded_count": 3,
  "documents": [...],
  "errors": []
}
```

## Semantic Search

### Search Capabilities

- **Natural Language Queries**: Ask questions in plain English
- **Semantic Understanding**: Finds relevant content even without exact keyword matches
- **Configurable Results**: Adjustable number of results (default: 5)
- **Similarity Scoring**: Results ranked by semantic similarity (0.0 to 1.0)

### Search Examples

```bash
# Find documents about AI
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is artificial intelligence?"}'

# Find machine learning content
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "How does machine learning work?", "n_results": 10}'
```

## Project Structure

```
docMgr/
├── app.py                    # Main FastAPI application
├── requirements.txt          # Python dependencies
├── repository/               # Repository layer
│   ├── vector_pipeline.py   # Vector processing and search
│   └── sqlDB.py             # Database operations
├── models/                   # Data models and DTOs
├── test_api.py              # API testing script
├── test_multiple_upload.py  # Multiple upload testing script
├── test_vector_pipeline.py  # Vector pipeline testing script
├── test_sentence_transformers.py  # Sentence-transformers testing script
├── test_pdf_support.py      # PDF testing script
├── test_docx_support.py     # DOCX testing script
├── test_image_processing.py # Image processing setup testing script
├── test_image_upload.py     # Image upload and processing testing script
├── env_example.txt          # Environment variables template
├── README.md                # This file
├── uploads/                 # File storage directory (created automatically)
├── chroma_db/              # Vector database (created automatically)
└── documents.db             # SQLite database (created automatically)
```

## Development

### Adding New Features

- **New Endpoints**: Add new route functions in `app.py`
- **Vector Processing**: Extend `vector_pipeline.py` for new file types
- **Database Changes**: Modify the `Document` model and run the application to auto-create tables
- **Validation**: Update Pydantic models for request/response validation

### Error Handling

The API includes comprehensive error handling:
- 400: Bad Request (e.g., missing file, unsupported file type)
- 404: Not Found (e.g., document doesn't exist)
- 500: Internal Server Error (database/file system issues)
- 503: Service Unavailable (vector pipeline not available)

## Security Considerations

- Files are stored with unique names to prevent path traversal attacks
- File content types are validated and stored
- Database connections are properly managed with dependency injection
- File operations include existence checks before deletion
- **Image Processing**: OCR and AI analysis done locally with secure API calls to Groq
- **API Key Security**: Groq API key stored in environment variables, never in code

## Troubleshooting

### Common Issues

1. **Vector pipeline not available:**
   ```bash
   # Check your dependencies installation
   python setup.py
   
   # Make sure all required packages are installed
   pip install -r requirements.txt
   ```

2. **Image processing not working:**
   ```bash
   # Check if Tesseract is installed
   tesseract --version
   
   # Check if Groq API key is set
   echo $GROQ_API_KEY
   
   # Test image processing setup
   python test_image_processing.py
   ```

2. **Port already in use:**
   ```bash
   # Kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

3. **Database locked:**
   - Ensure only one instance of the app is running
   - Check file permissions on the database file

4. **Upload directory issues:**
   - Ensure the application has write permissions to create the `uploads/` directory

5. **ChromaDB errors:**
   - Check if the `chroma_db/` directory has proper permissions
   - Restart the application to reinitialize the vector database

### Logs

Check the console output for detailed error messages and API request logs.

## Performance Considerations

- **Chunk Size**: 500 tokens provides good balance between context and search precision
- **Embedding Model**: all-MiniLM-L6-v2 offers excellent quality with local processing
- **Vector Database**: ChromaDB provides fast similarity search with local persistence
- **Batch Processing**: Multiple uploads are processed sequentially for reliability

## Future Enhancements

- **Additional File Types**: PowerPoint presentations, Excel spreadsheets, and other Office formats
- **Advanced Chunking**: Semantic chunking based on content structure
- **Hybrid Search**: Combine semantic search with keyword-based filtering
- **User Management**: Multi-user support with document access control
- **API Rate Limiting**: Protect against abuse and manage resource usage
- **Caching**: Redis-based caching for frequently accessed embeddings

## License

This project is open source and available under the MIT License.