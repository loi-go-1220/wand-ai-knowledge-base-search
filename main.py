from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Knowledge Base",
    description="Semantic search and Q&A system using OpenAI",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Basic health check"""
    return {
        "message": "AI Knowledge Base API", 
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    openai_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "healthy",
        "openai_configured": openai_key_configured,
        "endpoints": ["/", "/health", "/docs"]
    }

# TODO: Add actual endpoints as we build them
# - POST /documents/upload
# - POST /search  
# - POST /ask
# - GET /documents

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
