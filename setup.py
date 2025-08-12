#!/usr/bin/env python3
"""
Setup script for Document Manager API with Vector Pipeline
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["uploads", "chroma_db"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_env_file():
    """Check if .env file exists and guide user to create it"""
    env_file = Path(".env")
    example_file = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if example_file.exists():
        print("\n🔑 Environment setup required:")
        print("1. Copy the example environment file:")
        print(f"   cp {example_file} .env")
        print("2. Edit .env and add your Groq API key:")
        print("   GROQ_API_KEY=your_actual_api_key_here")
        print("3. Get your API key from: https://console.groq.com/")
        return False
    else:
        print("❌ Environment example file not found")
        return False

def test_imports():
    """Test if key modules can be imported"""
    print("\n🧪 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError:
        print("❌ FastAPI import failed")
        return False
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers import failed: {e}")
        # print("❌ Sentence Transformers import failed")
        return False
    
    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError:
        print("❌ ChromaDB import failed")
        return False
    
    try:
        import langchain_text_splitters
        print("✅ LangChain text splitters imported successfully")
    except ImportError:
        print("❌ LangChain text splitters import failed")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Document Manager API - Vector Pipeline Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check environment setup
    env_ready = check_env_file()
    
    # Test imports
    if not test_imports():
        print("\n❌ Some imports failed. Please check the installation.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    if env_ready:
        print("🎉 Setup completed successfully!")
        print("\nTo start the server:")
        print("  python app.py")
        print("\nTo test the vector pipeline:")
        print("  python test_vector_pipeline.py")
    else:
        print("⚠️  Setup partially completed.")
        print("Please complete the environment setup before running the application.")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
