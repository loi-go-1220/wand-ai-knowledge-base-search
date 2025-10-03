"""
FastAPI app for AI Knowledge Base
Now with actual functionality!
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os

from app.config import settings
from app.models import DocumentUpload, SearchQuery, SearchResult, QARequest, QAResponse
from app.document_processor import DocumentProcessor
from app.storage import storage

app = FastAPI(
    title="AI Knowledge Base",
    description="Semantic search and Q&A system using OpenAI",
    version="0.2.0"
)

processor = DocumentProcessor()

@app.get("/")
async def root():
    """Basic health check"""
    return {
        "message": "AI Knowledge Base API", 
        "status": "running",
        "version": "0.2.0",
        "stats": storage.get_stats()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "storage_stats": storage.get_stats(),
        "endpoints": ["/", "/health", "/docs", "/documents", "/upload", "/search"]
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    Basic implementation - only handles text files for now
    """
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        
        document = processor.process_document(file.filename, text_content)
        
        success = storage.store_document(document)
        
        if success:
            return {
                "message": "Document uploaded and processed successfully",
                "document_id": document.id,
                "filename": document.filename,
                "chunks_created": len(document.chunks)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store document")
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    documents = storage.list_documents()
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "chunks": len(doc.chunks),
                "processed": doc.processed,
                "created_at": doc.created_at
            }
            for doc in documents
        ],
        "total": len(documents)
    }

@app.post("/search", response_model=List[SearchResult])
async def search_documents(query: SearchQuery):
    """
    Semantic search through documents
    TODO: Add filtering and better ranking
    """
    try:
        query_embeddings = processor.generate_embeddings([query.query])
        
        if not query_embeddings or not query_embeddings[0]:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        results = storage.search_similar_chunks(query_embeddings[0], query.limit)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# TODO: Implement Q&A endpoint
# @app.post("/ask", response_model=QAResponse)
# async def ask_question(request: QARequest):
#     """Answer questions using retrieved context"""
#     pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)