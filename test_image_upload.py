#!/usr/bin/env python3
"""
Test script for image upload and processing
Tests the complete image processing pipeline through the API
"""

import os
import sys
import requests
from pathlib import Path

def test_image_upload():
    """Test image upload and processing through the API"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    upload_url = f"{base_url}/upload"
    
    # Check if uploads directory exists and contains images
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return False
    
    # Find image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(uploads_dir.glob(f"*{ext}"))
        image_files.extend(uploads_dir.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print("❌ No image files found in uploads/ directory")
        print("Please add some image files to test with")
        return False
    
    print(f"✅ Found {len(image_files)} image file(s) to test with")
    
    # Test with the first image file
    test_image = image_files[0]
    print(f"🧪 Testing with: {test_image.name}")
    
    # Check if API is running
    try:
        response = requests.get(f"{base_url}/docs")
        print("✅ API is running")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
        print("Please start the API with: uvicorn app:app --reload")
        return False
    
    # Upload the image
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (test_image.name, f, 'image/jpeg')}
            data = {'description': 'Test image upload for OCR processing'}
            
            print(f"📤 Uploading {test_image.name}...")
            response = requests.post(upload_url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Image upload successful!")
                print(f"   Document ID: {result['id']}")
                print(f"   Filename: {result['filename']}")
                print(f"   Content Type: {result['content_type']}")
                
                if result.get('processing_result'):
                    proc_result = result['processing_result']
                    print(f"   Processing Status: {proc_result.get('status', 'unknown')}")
                    if proc_result.get('total_chunks'):
                        print(f"   Total Chunks: {proc_result['total_chunks']}")
                    if proc_result.get('total_tokens'):
                        print(f"   Total Tokens: {proc_result['total_tokens']}")
                else:
                    print("   Processing Result: Not available")
                
                return True
            else:
                print(f"❌ Image upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def test_image_search():
    """Test searching for uploaded images"""
    
    base_url = "http://localhost:8000"
    search_url = f"{base_url}/search"
    
    # Test search with a generic query
    try:
        search_data = {
            "query": "image document",
            "limit": 5
        }
        
        print("\n🔍 Testing image search...")
        response = requests.post(search_url, json=search_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search successful!")
            print(f"   Found {len(result)} results")
            
            for i, doc in enumerate(result[:3]):  # Show first 3 results
                print(f"   {i+1}. {doc.get('original_filename', 'Unknown')} - {doc.get('content_type', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Image Upload and Processing...\n")
    
    # Test upload
    upload_success = test_image_upload()
    
    if upload_success:
        # Wait a bit for processing to complete
        import time
        print("\n⏳ Waiting for processing to complete...")
        time.sleep(3)
        
        # Test search
        search_success = test_image_search()
        
        if search_success:
            print("\n🎉 All image processing tests passed!")
        else:
            print("\n❌ Image search test failed")
    else:
        print("\n❌ Image upload test failed")
        sys.exit(1)
