#!/usr/bin/env python3
"""
Test script for image processing functionality
Tests OCR extraction and Groq API integration
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repository.vector_pipeline import VectorPipeline

def test_image_processing():
    """Test image processing with OCR and Groq API"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if Groq API key is available
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set GROQ_API_KEY in your .env file")
        return False
    
    print("✅ GROQ_API_KEY found")
    
    # Check if required libraries are available
    try:
        import PIL
        import pytesseract
        import cv2
        from groq import Groq
        print("✅ All required libraries are available")
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        print("Please install the required dependencies:")
        print("pip install Pillow pytesseract opencv-python groq")
        return False
    
    # Check if tesseract is installed on the system
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
    except Exception as e:
        print(f"❌ Tesseract OCR not available: {e}")
        print("Please install Tesseract OCR on your system:")
        print("macOS: brew install tesseract")
        print("Ubuntu: sudo apt-get install tesseract-ocr")
        print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    # Test Groq API connection
    try:
        groq_client = Groq(api_key=groq_api_key)
        # Simple test call
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ Groq API connection successful")
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False
    
    # Test vector pipeline initialization
    try:
        vector_pipeline = VectorPipeline()
        print("✅ Vector pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Vector pipeline initialization failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Image processing is ready to use.")
    print("\nTo test with an actual image:")
    print("1. Place an image file in the uploads/ directory")
    print("2. Use the API endpoint to upload and process the image")
    print("3. The image will be processed with OCR and Groq API description")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Image Processing Setup...\n")
    success = test_image_processing()
    
    if success:
        print("\n✅ Setup is complete and ready for image processing!")
    else:
        print("\n❌ Setup failed. Please fix the issues above.")
        sys.exit(1)
