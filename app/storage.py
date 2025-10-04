"""
Simple in-memory storage for MVP
TODO: Replace with proper database later
"""

from typing import List, Dict, Optional
from .models import Document, DocumentChunk, SearchResult
import numpy as np
from .cache import search_cache, cached
from .logger import logger, log_performance
import time

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
        Find similar chunks using cosine similarity with performance optimization
        """
        start_time = time.time()
        
        if not query_embedding:
            return []
        
        try:
            results = []
            query_vector = np.array(query_embedding)
            query_norm = np.linalg.norm(query_vector)
            
            # Pre-filter chunks with embeddings
            valid_chunks = [(chunk_id, chunk) for chunk_id, chunk in self.chunks.items() if chunk.embedding]
            
            if not valid_chunks:
                logger.warning("No chunks with embeddings found for search")
                return []
            
            # Vectorized similarity calculation for better performance
            chunk_vectors = np.array([chunk.embedding for _, chunk in valid_chunks])
            chunk_norms = np.linalg.norm(chunk_vectors, axis=1)
            
            # Calculate all similarities at once
            similarities = np.dot(chunk_vectors, query_vector) / (chunk_norms * query_norm)
            
            # Create results with similarity scores
            for i, (chunk_id, chunk) in enumerate(valid_chunks):
                similarity = float(similarities[i])
                
                # Skip very low similarity results for performance
                if similarity < 0.1:
                    continue
                
                # Get document filename for context
                doc = self.documents.get(chunk.document_id)
                doc_filename = doc.filename if doc else "Unknown"
                
                result = SearchResult(
                    chunk=chunk,
                    score=similarity,
                    document_filename=doc_filename
                )
                results.append(result)
            
            # Sort by similarity score (descending) and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            final_results = results[:limit]
            
            # Log performance
            duration = time.time() - start_time
            log_performance(
                "vector_search",
                duration,
                chunks_searched=len(valid_chunks),
                results_returned=len(final_results),
                query_limit=limit
            )
            
            return final_results
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Search failed after {duration:.2f}s: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get storage statistics"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "processed_documents": sum(1 for doc in self.documents.values() if doc.processed)
        }

storage = InMemoryStorage()
