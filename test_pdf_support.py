#!/usr/bin/env python3
"""
Test script for PDF support in the vector pipeline
"""

import requests
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_pdf_upload():
    """Test PDF document upload and processing"""
    print("🧪 Testing PDF Support")
    print("=" * 40)
    
    # Create a simple test PDF
    test_dir = Path("test_pdf")
    test_dir.mkdir(exist_ok=True)
    
    pdf_file = test_dir / "test_document.pdf"
    
    try:
        # Try to create a PDF using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(pdf_file), pagesize=letter)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 720, "This is a test PDF for the vector pipeline.")
        c.drawString(100, 700, "It contains text that should be extracted")
        c.drawString(100, 680, "and processed into embeddings.")
        c.drawString(100, 640, "The system should be able to:")
        c.drawString(100, 620, "1. Extract text from this PDF")
        c.drawString(100, 600, "2. Chunk the text appropriately")
        c.drawString(100, 580, "3. Generate embeddings for search")
        c.save()
        print("✅ Created test PDF document")
        
    except ImportError:
        print("⚠️  reportlab not available - creating text file instead")
        # Fallback to text file
        pdf_file = test_dir / "test_document.txt"
        with open(pdf_file, "w") as f:
            f.write("Test Document\nThis is a test document for the vector pipeline.")
    
    # Test upload
    print(f"\n📤 Uploading {pdf_file.name}...")
    
    try:
        with open(pdf_file, "rb") as f:
            files = {"file": (pdf_file.name, f.read(), "application/pdf")}
            data = {"description": "Test PDF document for vector processing"}
            
            response = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data)
            
            if response.status_code == 200:
                doc_info = response.json()
                print(f"✅ Upload successful! Document ID: {doc_info['id']}")
                
                # Check vector processing
                if doc_info.get("processing_result"):
                    proc_result = doc_info["processing_result"]
                    if proc_result["status"] == "processed":
                        print(f"   📊 Vector processing successful:")
                        print(f"      - Chunks: {proc_result['total_chunks']}")
                        print(f"      - Tokens: {proc_result['total_tokens']}")
                    else:
                        print(f"   ⚠️  Vector processing failed: {proc_result.get('error', 'Unknown error')}")
                else:
                    print("   ℹ️  No vector processing result available")
                
                # Test search functionality
                print(f"\n🔍 Testing search functionality...")
                search_data = {"query": "test document vector pipeline", "n_results": 3}
                search_response = requests.post(f"{BASE_URL}/api/search", json=search_data)
                
                if search_response.status_code == 200:
                    results = search_response.json()
                    print(f"   ✅ Search successful! Found {len(results)} results")
                    for i, result in enumerate(results[:2]):
                        score = result['similarity_score']
                        filename = result['metadata']['original_filename']
                        print(f"      {i+1}. {filename} (Score: {score:.3f})")
                else:
                    print(f"   ❌ Search failed: {search_response.status_code}")
                
                # Clean up - delete the document
                print(f"\n🧹 Cleaning up test document...")
                delete_response = requests.delete(f"{BASE_URL}/api/documents/{doc_info['id']}")
                if delete_response.status_code == 200:
                    print("   ✅ Document deleted successfully")
                else:
                    print(f"   ❌ Failed to delete document: {delete_response.status_code}")
                
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    # Clean up test files
    try:
        if pdf_file.exists():
            os.remove(pdf_file)
        if test_dir.exists() and not any(test_dir.iterdir()):
            test_dir.rmdir()
    except:
        pass
    
    print("\n" + "=" * 40)
    print("🎉 PDF Support Test Completed!")

if __name__ == "__main__":
    print("Document Manager API - PDF Support Test")
    print("Make sure the server is running and PDF dependencies are installed")
    print("=" * 40)
    
    test_pdf_upload()
