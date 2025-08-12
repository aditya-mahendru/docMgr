"""
Vector Pipeline for Document Ingestion
Handles document chunking, embedding generation, and vector storage
"""

from typing import List, Dict, Any, Optional
import markdown
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

class VectorPipeline:
    def __init__(self):
        """Initialize the vector pipeline with sentence-transformers and ChromaDB"""
        # Initialize sentence-transformers model
        print("🔄 Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence transformer model loaded successfully")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Tokenizer for counting tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.tokenizer.encode(text))
    
    def _extract_text_from_file(self, file_path: str, content_type: str) -> str:
        """Extract text content from different file types"""
        try:
            if content_type == "text/plain" or file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif content_type == "text/markdown" or file_path.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                    # Convert markdown to plain text for processing
                    html = markdown.markdown(md_content)
                    # Simple HTML to text conversion (remove tags)
                    import re
                    text = re.sub(r'<[^>]+>', '', html)
                    return text
            
            else:
                raise ValueError(f"Unsupported file type: {content_type}")
                
        except Exception as e:
            raise Exception(f"Error extracting text from file: {str(e)}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """Break text into chunks using LangChain splitter"""
        return self.text_splitter.split_text(text)
    
    def _generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks using sentence-transformers"""
        try:
            # Generate embeddings locally using sentence-transformers
            embeddings = self.embedding_model.encode(chunks, convert_to_tensor=False)
            # Convert to list of lists of floats
            if hasattr(embeddings, 'tolist'):
                return embeddings.tolist()
            elif isinstance(embeddings, list):
                return embeddings
            else:
                # Handle numpy array case
                import numpy as np
                if isinstance(embeddings, np.ndarray):
                    return embeddings.tolist()
                else:
                    # Fallback: convert to list
                    return [list(emb) for emb in embeddings]
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def process_document(self, file_path: str, content_type: str, document_id: int, 
                        original_filename: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Process a document through the vector pipeline"""
        try:
            # Extract text from file
            text = self._extract_text_from_file(file_path, content_type)
            
            # Chunk the text
            chunks = self._chunk_text(text)
            
            # Generate embeddings
            embeddings = self._generate_embeddings(chunks)
            
            # Store in vector database
            chunk_ids = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{document_id}_{i}"
                chunk_ids.append(chunk_id)
                
                # Prepare metadata, ensuring no None values
                metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "original_filename": original_filename,
                    "content_type": content_type,
                    "description": description or "",  # Convert None to empty string
                    "chunk_size": self._count_tokens(chunk),
                    "total_chunks": len(chunks)
                }
                
                # Store chunk metadata and embedding
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[chunk_id]
                )
            
            return {
                "document_id": document_id,
                "original_filename": original_filename,
                "total_chunks": len(chunks),
                "total_tokens": sum(self._count_tokens(chunk) for chunk in chunks),
                "chunk_ids": chunk_ids,
                "status": "processed"
            }
            
        except Exception as e:
            return {
                "document_id": document_id,
                "original_filename": original_filename,
                "status": "error",
                "error": str(e)
            }
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents by semantic similarity"""
        try:
            # Generate embedding for query
            query_embedding = self._generate_embeddings([query])[0]
            
            # Search in vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and 'ids' in results and results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "chunk_id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "similarity_score": 1 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Error searching documents: {str(e)}")
    
    def get_document_chunks(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"]
            )
            
            chunks = []
            if results and 'ids' in results and results['ids']:
                for i in range(len(results['ids'])):
                    chunks.append({
                        "chunk_id": results['ids'][i],
                        "content": results['documents'][i],
                        "metadata": results['metadatas'][i]
                    })
            
            return sorted(chunks, key=lambda x: x['metadata']['chunk_index'])
            
        except Exception as e:
            raise Exception(f"Error retrieving document chunks: {str(e)}")
    
    def delete_document_chunks(self, document_id: int) -> bool:
        """Delete all chunks for a specific document"""
        try:
            # Get chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id},
                include=[]
            )
            
            if results and 'ids' in results and results['ids']:
                self.collection.delete(ids=results['ids'])
            
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting document chunks: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            count = self.collection.count()
            
            # Get sample metadata to understand structure
            sample = self.collection.get(limit=1, include=["metadatas"])
            
            return {
                "total_chunks": count,
                "collection_name": "documents",
                "sample_metadata": sample and 'metadatas' in sample and sample['metadatas'][0] if sample['metadatas'] else None
            }
            
        except Exception as e:
            return {"error": str(e)}
