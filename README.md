# Document Manager (DocMgr)

A powerful document management system with AI-powered semantic search, OCR processing, and vector-based document analysis. Built with FastAPI, SQLite, and ChromaDB for intelligent document processing and retrieval.

## 🚀 Features

- **📁 File Management**: Upload, retrieve, list, and delete documents
- **🔍 Semantic Search**: AI-powered search across document content using vector embeddings
- **📸 Image Processing**: OCR extraction and AI-powered description generation
- **🧠 Vector Pipeline**: Intelligent document chunking and semantic indexing
- **📊 Multiple Formats**: Support for PDF, DOCX, TXT, MD, and image files
- **⚡ Fast API**: RESTful endpoints with async processing
- **💾 Local Storage**: SQLite database + ChromaDB vector store
- **🔐 User Management**: Authentication and authorization system

## 🏗️ Architecture

```
docMgr/
├── app.py                 # FastAPI main application
├── db.py                  # Database models and setup
├── models/                # Data models and DTOs
├── repository/            # Business logic and API handlers
├── chroma_db/            # Vector database storage
├── uploads/              # Document file storage
├── documents.db          # SQLite metadata database
└── setup_*.py            # Setup and configuration scripts
```

## 📋 Prerequisites

- **Python 3.8+**
- **Tesseract OCR** (for image processing)
- **Groq API key** (for AI image descriptions)
- **Git** (for cloning)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd docMgr
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your settings
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Install Tesseract OCR

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
```

#### Windows
Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

#### Automated Setup (Recommended)
```bash
python setup_image_processing.py
```

### 6. Initialize Database
```bash
python setup.py
```

## 🚀 Quick Start

### Start the Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📚 Sample Data & Testing

### 1. Sample Documents
The repository includes sample documents for testing:
- `AI_Text.txt` - Sample AI-related content
- Test scripts for various file formats

### 2. Test the API
```bash
# Test basic functionality
python test_api.py

# Test specific features
python test_pdf_support.py
python test_image_processing.py
python test_user_management.py
```

### 3. Sample API Calls

#### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_document.pdf" \
  -F "description=Sample document for testing"
```

#### Search Documents
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "n_results": 5}'
```

#### Get Document Chunks
```bash
curl "http://localhost:8000/api/documents/1/chunks"
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for AI processing | Required |
| `UPLOAD_DIR` | Document upload directory | `./uploads` |
| `CHROMA_PERSIST_DIR` | Vector database directory | `./chroma_db` |
| `DATABASE_URL` | SQLite database path | `./documents.db` |

### Database Schema
- **Documents**: Metadata, file paths, processing status
- **Chunks**: Text segments with vector embeddings
- **Users**: Authentication and authorization data

## 📖 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and health check |
| `POST` | `/api/documents/upload` | Upload single document |
| `POST` | `/api/documents/upload-multiple` | Upload multiple documents |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document details |
| `DELETE` | `/api/documents/{id}` | Delete document |
| `POST` | `/api/search` | Semantic search across documents |
| `GET` | `/api/documents/{id}/chunks` | Get document chunks |
| `GET` | `/api/vector/stats` | Vector database statistics |

### Search Parameters
- `query`: Search text (required)
- `n_results`: Number of results (default: 5, max: 20)
- `threshold`: Similarity threshold (default: 0.5)

## 🧪 Testing

### Run All Tests
```bash
# Test API endpoints
python test_api.py

# Test file format support
python test_pdf_support.py
python test_docx_support.py
python test_image_processing.py

# Test vector pipeline
python test_vector_pipeline.py

# Test user management
python test_user_management.py
```

### Test Coverage
- ✅ API endpoints
- ✅ File uploads (PDF, DOCX, TXT, images)
- ✅ Vector search functionality
- ✅ User authentication
- ✅ Image processing and OCR

## 🚨 Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
```bash
# Verify installation
tesseract --version

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

#### 2. Vector Search Not Working
```bash
# Check ChromaDB directory
ls -la chroma_db/

# Reinitialize vector store
python setup.py
```

#### 3. Image Processing Errors
```bash
# Verify Groq API key
echo $GROQ_API_KEY

# Check image file format support
python test_image_processing.py
```

### Performance Tips
- Use SSD storage for better vector search performance
- Limit concurrent uploads to prevent memory issues
- Monitor ChromaDB directory size for large document collections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check the `/docs` endpoint when running
- **Testing**: Use the provided test scripts to verify functionality

## 🔄 Updates & Maintenance

### Regular Maintenance
- Monitor ChromaDB directory size
- Clean up old uploads periodically
- Update dependencies regularly
- Backup SQLite database

### Version Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Check for breaking changes
python test_api.py
```

---

**Ready to get started?** Follow the installation steps above and run `python setup.py` to initialize your system!