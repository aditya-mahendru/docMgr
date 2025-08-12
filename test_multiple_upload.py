#!/usr/bin/env python3
"""
Test script for multiple document upload functionality
"""

import requests
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def create_test_files():
    """Create some test files for upload"""
    test_files = []
    
    # Create test directory if it doesn't exist
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create some test text files
    test_content = [
        ("document1.txt", "This is the first test document content."),
        ("document2.txt", "This is the second test document content."),
        ("document3.txt", "This is the third test document content."),
    ]
    
    for filename, content in test_content:
        file_path = test_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
        test_files.append(str(file_path))
    
    return test_files

def test_multiple_upload():
    """Test the multiple document upload endpoint"""
    print("Testing multiple document upload...")
    
    # Create test files
    test_files = create_test_files()
    print(f"Created {len(test_files)} test files")
    
    # Prepare files for upload
    files = []
    for file_path in test_files:
        with open(file_path, "rb") as f:
            files.append(("files", (os.path.basename(file_path), f.read(), "text/plain")))
    
    # Make the request
    url = f"{BASE_URL}/api/documents/upload-multiple"
    data = {"description": "Bulk upload test"}
    
    try:
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"Message: {result['message']}")
            print(f"Uploaded count: {result['uploaded_count']}")
            print(f"Documents uploaded:")
            for doc in result['documents']:
                print(f"  - {doc['original_filename']} (ID: {doc['id']})")
            
            if result['errors']:
                print(f"Errors encountered:")
                for error in result['errors']:
                    print(f"  - {error}")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error during upload: {e}")
    
    # Clean up test files
    print("\nCleaning up test files...")
    for file_path in test_files:
        try:
            os.remove(file_path)
        except:
            pass
    
    # Remove test directory if empty
    try:
        test_dir = Path("test_files")
        if test_dir.exists() and not any(test_dir.iterdir()):
            test_dir.rmdir()
    except:
        pass

def test_single_upload():
    """Test the single document upload endpoint for comparison"""
    print("\nTesting single document upload...")
    
    # Create a single test file
    test_file = "single_test.txt"
    with open(test_file, "w") as f:
        f.write("This is a single test document.")
    
    # Prepare file for upload
    with open(test_file, "rb") as f:
        files = {"file": (test_file, f.read(), "text/plain")}
    
    # Make the request
    url = f"{BASE_URL}/api/documents/upload"
    data = {"description": "Single upload test"}
    
    try:
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single upload successful!")
            print(f"Document: {result['original_filename']} (ID: {result['id']})")
        else:
            print(f"❌ Single upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error during single upload: {e}")
    
    # Clean up
    try:
        os.remove(test_file)
    except:
        pass

if __name__ == "__main__":
    print("Document Manager API - Multiple Upload Test")
    print("=" * 50)
    
    # Test single upload first
    test_single_upload()
    
    # Test multiple upload
    test_multiple_upload()
    
    print("\n" + "=" * 50)
    print("Test completed!")
