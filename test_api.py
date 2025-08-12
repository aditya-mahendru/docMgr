#!/usr/bin/env python3
"""
Test script for the Document Manager API
"""
import requests
import os
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_upload():
    """Test document upload"""
    print("Testing document upload...")
    
    # Create a test file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test document for the API.")
    
    # Upload the file
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        data = {"description": "Test document for API testing"}
        response = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data)
    
    print(f"Upload Status: {response.status_code}")
    if response.status_code == 200:
        doc_data = response.json()
        print(f"Uploaded Document ID: {doc_data['id']}")
        print(f"Original Filename: {doc_data['original_filename']}")
        print(f"File Size: {doc_data['file_size']} bytes")
        return doc_data['id']
    else:
        print(f"Upload failed: {response.text}")
        return None
    
    # Clean up test file
    os.remove(test_file_path)

def test_list_documents():
    """Test listing all documents"""
    print("Testing list documents...")
    response = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        documents = response.json()
        print(f"Found {len(documents)} documents:")
        for doc in documents:
            print(f"  - ID: {doc['id']}, Name: {doc['original_filename']}, Size: {doc['file_size']} bytes")
    else:
        print(f"Failed to list documents: {response.text}")
    print()

def test_get_document(doc_id):
    """Test getting a specific document"""
    print(f"Testing get document {doc_id}...")
    response = requests.get(f"{BASE_URL}/api/documents/{doc_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        doc = response.json()
        print(f"Document: {json.dumps(doc, indent=2)}")
    else:
        print(f"Failed to get document: {response.text}")
    print()

def test_delete_document(doc_id):
    """Test deleting a document"""
    print(f"Testing delete document {doc_id}...")
    response = requests.delete(f"{BASE_URL}/api/documents/{doc_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Failed to delete document: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=== Document Manager API Test Suite ===\n")
    
    try:
        # Test root endpoint
        test_root()
        
        # Test upload
        doc_id = test_upload()
        
        if doc_id:
            # Test list documents
            test_list_documents()
            
            # Test get specific document
            test_get_document(doc_id)
            
            # Test delete document
            test_delete_document(doc_id)
            
            # Verify deletion by listing again
            print("Verifying deletion...")
            test_list_documents()
        
        print("=== Test Suite Completed ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
        print("Run: python app.py")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
