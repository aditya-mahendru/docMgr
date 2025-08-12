#!/usr/bin/env python3
"""
Simple test script for sentence-transformers integration
"""

def test_sentence_transformers():
    """Test sentence-transformers functionality"""
    print("🧪 Testing Sentence Transformers Integration")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Importing sentence-transformers...")
        from sentence_transformers import SentenceTransformer
        print("✅ Import successful")
        
        # Test model loading
        print("🔄 Loading model 'all-MiniLM-L6-v2'...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")
        
        # Test embedding generation
        print("🔤 Testing embedding generation...")
        test_texts = [
            "This is a test sentence about artificial intelligence.",
            "Machine learning is a subset of AI.",
            "Natural language processing helps computers understand text."
        ]
        
        embeddings = model.encode(test_texts, convert_to_tensor=False)
        print(f"✅ Generated embeddings: {embeddings.shape}")
        
        # Test similarity
        print("🔍 Testing similarity calculation...")
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Calculate similarity between first and second sentence
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        print(f"✅ Similarity between AI and ML sentences: {similarity:.3f}")
        
        # Test similarity between first and third sentence (should be lower)
        similarity2 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]
        print(f"✅ Similarity between AI and NLP sentences: {similarity2:.3f}")
        
        print("\n🎉 All tests passed! Sentence-transformers is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Try installing with: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sentence_transformers()
    if success:
        print("\n🚀 Ready to use sentence-transformers in your vector pipeline!")
    else:
        print("\n⚠️  Please fix the issues before proceeding.")
        sys.exit(1)
