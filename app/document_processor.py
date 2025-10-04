"""
Document processing and chunking
This is where the magic happens - turning docs into searchable chunks
"""

import re
import uuid
from typing import List
from datetime import datetime
from openai import OpenAI

from .models import Document, DocumentChunk
from .config import settings
from .cache import embedding_cache, cached

class DocumentProcessor:
    """Handles document processing and embedding generation"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Improved text chunking - handles different content types
        """
        text = text.strip()
        
        if '\n\n' in text:
            return self._chunk_by_paragraphs(text)
        else:
            print("   No paragraph breaks found, using line-based chunking")
            return self._chunk_by_lines(text)
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """Original paragraph-based chunking"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            estimated_tokens = len(current_chunk + paragraph) // 4
            
            if estimated_tokens > settings.MAX_CHUNK_SIZE and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_lines(self, text: str) -> List[str]:
        """Line-based chunking for transcripts, code, etc."""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            test_chunk = current_chunk + "\n" + line if current_chunk else line
            estimated_tokens = len(test_chunk) // 4
            
            if estimated_tokens > settings.MAX_CHUNK_SIZE and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                if current_chunk:
                    current_chunk += "\n" + line
                else:
                    current_chunk = line
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @cached(ttl=86400, cache_instance=embedding_cache)  # Cache for 24 hours
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with better error handling
        """
        if not texts:
            return []
            
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text.strip()]
        if not valid_texts:
            print("⚠️  No valid texts to embed")
            return [[] for _ in texts]
        
        try:
            # Batch size limit for OpenAI API
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                print(f"   Generating embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")
                
                response = self.client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            if "rate_limit" in str(e).lower():
                print("   Rate limit hit - consider adding delays between requests")
            elif "invalid_request" in str(e).lower():
                print("   Invalid request - check text content and length")
            
            # Return empty embeddings to prevent crashes
            return [[] for _ in texts]
    
    def process_document(self, filename: str, content: str) -> Document:
        """
        Process a document: chunk it and generate embeddings
        """
        print(f"📄 Processing document: {filename}")
        
        doc_id = str(uuid.uuid4())
        document = Document(
            id=doc_id,
            filename=filename,
            content=content,
            created_at=datetime.now(),
            processed=False
        )
        
        chunks = self.chunk_text(content)
        print(f"   Split into {len(chunks)} chunks")
        
        print(f"   Generating embeddings...")
        embeddings = self.generate_embeddings(chunks)
        
        document_chunks = []
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                chunk_text=chunk_text,
                chunk_index=i,
                embedding=embedding,
                created_at=datetime.now()
            )
            document_chunks.append(chunk)
        
        document.chunks = document_chunks
        document.processed = True
        
        print(f"Document processed successfully!")
        return document
