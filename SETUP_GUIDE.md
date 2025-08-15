# DocMgr Setup Guide

This guide will walk you through setting up the DocMgr document management system from scratch, including all dependencies, sample data, and testing.

## 🎯 Quick Start (5 minutes)

If you want to get up and running quickly:

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd docMgr

# 2. Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Setup environment
cp env_example.txt .env
# Edit .env with your GROQ_API_KEY

# 4. Install Tesseract OCR
python setup_image_processing.py

# 5. Initialize system
python setup.py

# 6. Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 7. Load sample data (in new terminal)
python setup_sample_data.py
```

## 📋 Detailed Setup Instructions

### Prerequisites

#### System Requirements
- **Operating System**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Memory**: At least 4GB RAM (8GB recommended)
- **Storage**: 2GB free space for dependencies and sample data

#### Required Software
- **Python 3.8+**: [Download from python.org](https://www.python.org/downloads/)
- **Git**: [Download from git-scm.com](https://git-scm.com/downloads)
- **Tesseract OCR**: Required for image processing

### Step 1: Environment Setup

#### 1.1 Clone the Repository
```bash
git clone <your-repo-url>
cd docMgr
```

#### 1.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

#### 1.3 Install Python Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 2: External Dependencies

#### 2.1 Install Tesseract OCR

**macOS (using Homebrew):**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
1. Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. Restart terminal/command prompt

**Automated Setup (Recommended):**
```bash
python setup_image_processing.py
```

#### 2.2 Verify Tesseract Installation
```bash
tesseract --version
```

### Step 3: Configuration

#### 3.1 Environment Variables
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
# Groq API key for AI-powered image processing
GROQ_API_KEY=your_groq_api_key_here

# Optional: Custom paths
UPLOAD_DIR=./uploads
CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=./documents.db
```

**Getting a Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### 3.2 Database Initialization
```bash
# Initialize database and create tables
python setup.py
```

### Step 4: System Startup

#### 4.1 Start the Server
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Alternative startup methods:**
```bash
# Using Python directly
python app.py

# Production mode (no auto-reload)
uvicorn app:app --host 0.0.0.0 --port 8000
```

#### 4.2 Verify Server is Running
```bash
# Test API endpoint
curl http://localhost:8000/

# Expected response: API information JSON
```

### Step 5: Sample Data Setup

#### 5.1 Load Sample Documents
```bash
# In a new terminal, with virtual environment activated
cd docMgr
source .venv/bin/activate

# Run sample data setup
python setup_sample_data.py
```

This script will:
- Create sample text files with AI/ML content
- Upload them to the DocMgr system
- Initialize the vector pipeline
- Run health checks

#### 5.2 Verify Sample Data
```bash
# Check documents endpoint
curl http://localhost:8000/api/documents

# Check vector stats
curl http://localhost:8000/api/vector/stats

# Test search functionality
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "n_results": 3}'
```

### Step 6: Testing

#### 6.1 Run Test Suite
```bash
# Test basic API functionality
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

#### 6.2 Manual Testing
```bash
# Test file upload
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@AI_Text.txt" \
  -F "description=Test document"

# Test semantic search
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning algorithms", "n_results": 5}'
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
```bash
# Check if Tesseract is installed
tesseract --version

# If not found, add to PATH
export PATH="/usr/local/bin:$PATH"

# Or reinstall using the setup script
python setup_image_processing.py
```

#### 2. Database Errors
```bash
# Remove existing database and reinitialize
rm documents.db
python setup.py
```

#### 3. Vector Pipeline Issues
```bash
# Check ChromaDB directory
ls -la chroma_db/

# Reinitialize vector store
python setup.py
```

#### 4. Port Already in Use
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

#### 5. Permission Errors
```bash
# Check file permissions
ls -la uploads/ chroma_db/

# Fix permissions if needed
chmod 755 uploads/ chroma_db/
```

### Performance Issues

#### 1. Slow Vector Search
- Ensure you're using SSD storage
- Check available RAM (8GB+ recommended)
- Monitor ChromaDB directory size

#### 2. Large File Processing
- Limit concurrent uploads
- Monitor memory usage
- Use appropriate chunk sizes

## 📊 System Verification

### Health Check Endpoints
```bash
# API information
curl http://localhost:8000/

# Health status
curl http://localhost:8000/health

# Document count
curl http://localhost:8000/api/documents | jq 'length'

# Vector database stats
curl http://localhost:8000/api/vector/stats
```

### Expected Outputs
- **API Info**: JSON with endpoint descriptions
- **Documents**: Array of document objects
- **Vector Stats**: Collection information and chunk counts

## 🚀 Next Steps

After successful setup:

1. **Explore the API**: Visit `http://localhost:8000/docs` for interactive documentation
2. **Upload Documents**: Test with various file formats
3. **Try Semantic Search**: Ask questions about your documents
4. **Set up Chatbot**: Configure the DocMgr-llm chatbot interface
5. **Customize**: Modify configuration for your specific needs

## 📚 Additional Resources

- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **ChromaDB Documentation**: [docs.trychroma.com](https://docs.trychroma.com/)
- **Tesseract Documentation**: [github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
- **Groq API Documentation**: [console.groq.com/docs](https://console.groq.com/docs)

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the terminal
2. **Verify prerequisites**: Ensure all dependencies are installed
3. **Check configuration**: Verify environment variables and file paths
4. **Run tests**: Use the provided test scripts to isolate issues
5. **Create an issue**: Report bugs with detailed error messages

---

**Happy Document Managing! 🎉**
