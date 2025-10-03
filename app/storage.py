"""
Simple in-memory storage for MVP
TODO: Replace with proper database later
"""

from typing import List, Dict, Optional
from .models import Document, DocumentChunk, SearchResult
import numpy as np

class InMemoryStorage:
    """
    Simple in-memory storage for documents and embeddings
    Good enough for demo - will replace with proper DB later
    """
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, DocumentChunk] = {}
        print("Initialized in-memory storage")
    
    def store_document(self, document: Document) -> bool:
        """Store a processed document"""
        try:
            self.documents[document.id] = document
            
            for chunk in document.chunks:
                self.chunks[chunk.id] = chunk
            
            print(f"💾 Stored document: {document.filename} ({len(document.chunks)} chunks)")
            return True
            
        except Exception as e:
            print(f"Failed to store document: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID"""
        return self.documents.get(doc_id)
    
    def list_documents(self) -> List[Document]:
        """List all stored documents"""
        return list(self.documents.values())
    
    def search_similar_chunks(self, query_embedding: List[float], limit: int = 5) -> List[SearchResult]:
        """
        Find similar chunks using cosine similarity
        Very basic implementation - good enough for MVP
        """
        if not query_embedding:
            return []
        
        results = []
        query_vector = np.array(query_embedding)
        
        for chunk in self.chunks.values():
            if not chunk.embedding:
                continue
                
            chunk_vector = np.array(chunk.embedding)
            
            similarity = np.dot(query_vector, chunk_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(chunk_vector)
            )
            
            doc = self.documents.get(chunk.document_id)
            doc_filename = doc.filename if doc else "Unknown"
            
            result = SearchResult(
                chunk=chunk,
                score=float(similarity),
                document_filename=doc_filename
            )
            results.append(result)
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def get_stats(self) -> dict:
        """Get storage statistics"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "processed_documents": sum(1 for doc in self.documents.values() if doc.processed)
        }

storage = InMemoryStorage()
