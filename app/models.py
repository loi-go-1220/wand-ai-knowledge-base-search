"""
Data models for the knowledge base
Quick and dirty models - will refine as we go
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    """Model for document upload request"""
    filename: str
    content: str
    # TODO: Add file type validation later

class DocumentChunk(BaseModel):
    """Represents a chunk of a document with embedding"""
    id: Optional[str] = None
    document_id: str
    chunk_text: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None

class Document(BaseModel):
    """Document metadata"""
    id: Optional[str] = None
    filename: str
    content: str
    chunks: Optional[List[DocumentChunk]] = []
    created_at: Optional[datetime] = None
    processed: bool = False

class SearchQuery(BaseModel):
    """Search request model"""
    query: str
    limit: int = 5
    # TODO: Add filters later

class SearchResult(BaseModel):
    """Search result with relevance score"""
    chunk: DocumentChunk
    score: float
    document_filename: str

class QARequest(BaseModel):
    """Q&A request model"""
    question: str
    context_limit: int = 3

class QAResponse(BaseModel):
    """Q&A response with sources"""
    answer: str
    sources: List[SearchResult]
    confidence: Optional[float] = None
