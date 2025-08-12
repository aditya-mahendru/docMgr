# Document Manager API

A FastAPI-based document management system with SQLite backend that supports file upload, retrieval, listing, and deletion.

## Features

- **File Upload**: Upload documents with optional descriptions
- **Document Listing**: Get all uploaded documents
- **Document Retrieval**: Get specific document details by ID
- **Document Deletion**: Remove documents from the system
- **SQLite Database**: Local database storage for document metadata
- **File Storage**: Secure file storage with unique filenames
- **RESTful API**: Clean, REST-compliant endpoints

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `POST` | `/api/documents/upload` | Upload a new document |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document details by ID |
| `DELETE` | `/api/documents/{id}` | Delete document by ID |

## Setup

### Prerequisites

- Python 3.8+
- pip (Python package installer)

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

1. **Run the test script:**
   ```bash
   python test_api.py
   ```

2. **Manual testing with curl:**
   ```bash
   # Get API info
   curl http://localhost:8000/
   
   # Upload a document
   curl -X POST "http://localhost:8000/api/documents/upload" \
        -F "file=@/path/to/your/document.pdf" \
        -F "description=My important document"
   
   # List all documents
   curl http://localhost:8000/api/documents
   
   # Get specific document
   curl http://localhost:8000/api/documents/1
   
   # Delete document
   curl -X DELETE http://localhost:8000/api/documents/1
   ```

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

## File Storage

- Files are stored in the `uploads/` directory
- Unique filenames are generated using UUID to prevent conflicts
- Original filenames are preserved in the database
- File paths are stored relative to the application root

## Project Structure

```
docMgr/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── test_api.py        # API testing script
├── README.md          # This file
├── uploads/           # File storage directory (created automatically)
└── documents.db       # SQLite database (created automatically)
```

## Development

### Adding New Features

- **New Endpoints**: Add new route functions in `app.py`
- **Database Changes**: Modify the `Document` model and run the application to auto-create tables
- **Validation**: Update Pydantic models for request/response validation

### Error Handling

The API includes comprehensive error handling:
- 400: Bad Request (e.g., missing file)
- 404: Not Found (e.g., document doesn't exist)
- 500: Internal Server Error (database/file system issues)

## Security Considerations

- Files are stored with unique names to prevent path traversal attacks
- File content types are validated and stored
- Database connections are properly managed with dependency injection
- File operations include existence checks before deletion

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database locked:**
   - Ensure only one instance of the app is running
   - Check file permissions on the database file

3. **Upload directory issues:**
   - Ensure the application has write permissions to create the `uploads/` directory

### Logs

Check the console output for detailed error messages and API request logs.

## License

This project is open source and available under the MIT License.