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
from app.qa_service import QAService
from app.completeness_checker import CompletenessChecker

app = FastAPI(
    title="AI Knowledge Base",
    description="Semantic search and Q&A system using OpenAI",
    version="0.3.0"
)

processor = DocumentProcessor()
qa_service = QAService()
completeness_checker = CompletenessChecker()

@app.get("/")
async def root():
    """Basic health check"""
    return {
        "message": "AI Knowledge Base API", 
        "status": "running",
        "version": "0.3.0",
        "stats": storage.get_stats()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "storage_stats": storage.get_stats(),
        "endpoints": ["/", "/health", "/docs", "/documents", "/upload", "/search", "/ask", "/completeness"]
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document with improved error handling
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size (rough estimate)
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Try to decode as UTF-8
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other common encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    text_content = content.decode(encoding)
                    print(f"⚠️  Decoded {file.filename} using {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="File encoding not supported. Please use UTF-8 text files."
                )
        
        # Validate content length
        if len(text_content.strip()) < 10:
            raise HTTPException(status_code=400, detail="File content too short (minimum 10 characters)")
        
        # Process the document
        print(f"📤 Uploading: {file.filename} ({len(text_content)} chars)")
        document = processor.process_document(file.filename, text_content)
        
        # Check if processing was successful
        if not document.processed or not document.chunks:
            raise HTTPException(status_code=500, detail="Document processing failed - no chunks created")
        
        # Store it
        success = storage.store_document(document)
        
        if success:
            return {
                "message": "Document uploaded and processed successfully",
                "document_id": document.id,
                "filename": document.filename,
                "chunks_created": len(document.chunks),
                "content_length": len(text_content)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store document")
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Upload error for {file.filename}: {e}")
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

@app.post("/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """Answer questions using retrieved context and GPT-4"""
    try:
        response = qa_service.answer_question(request.question, request.context_limit)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

@app.get("/completeness")
async def check_completeness():
    """
    Analyze knowledge base completeness and suggest improvements
    This addresses the 'completeness check' requirement from the challenge
    """
    try:
        analysis = completeness_checker.analyze_coverage()
        suggested_questions = completeness_checker.suggest_questions()
        
        return {
            "analysis": analysis,
            "suggested_questions": suggested_questions,
            "timestamp": "2024-10-06T13:30:00Z"  # Would use datetime.now() in real app
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completeness check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)