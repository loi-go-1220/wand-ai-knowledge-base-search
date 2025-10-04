# System Architecture

## Overview

Architecture decisions and trade-offs for the AI knowledge base system.

## System Design

```
Client ──► FastAPI ──► Business Logic ──► Storage
                │            │             │
                │            └──► OpenAI API
                └──► Auto Docs
```

**Layers:**
- **API**: FastAPI with validation and error handling
- **Business**: DocumentProcessor, QAService, CompletenessChecker  
- **Storage**: In-memory vectors and metadata
- **External**: OpenAI embeddings and GPT-4

## Components

### FastAPI App (`main.py`)
- HTTP routing and validation
- Auto-generated docs
- File upload handling
- Error responses

### Document Processor (`app/document_processor.py`)
- **Intelligent chunking**: Paragraphs vs lines detection
- **Batch embeddings**: 100 texts per OpenAI call
- **Token estimation**: ~4 chars per token

```python
# Auto-detects content type
if '\n\n' in text:
    return chunk_by_paragraphs(text)  # Documents
else:
    return chunk_by_lines(text)       # Transcripts
```

### Vector Storage (`app/storage.py`)
- In-memory document and embedding storage
- Cosine similarity search with NumPy
- Metadata tracking and statistics

### Q&A Service (`app/qa_service.py`)
- Context retrieval via semantic search
- GPT-4 answer generation
- Confidence scoring
- Source attribution

### Completeness Checker (`app/completeness_checker.py`)
- Knowledge gap analysis
- Topic coverage metrics
- Improvement suggestions

## Key Decisions

### In-Memory Storage
- **Why**: Fast development, no DB setup, excellent demo performance
- **Trade-off**: Data lost on restart, single instance only

### Simple Token Estimation  
- **Why**: 4 chars ≈ 1 token is fast and good enough for chunking
- **Trade-off**: Not precise for all languages

### Batch Processing
- **Why**: Efficient OpenAI API usage, respects rate limits
- **Trade-off**: Slightly more complex code

## Performance

- **Upload**: 2-5 seconds per document
- **Search**: <100ms in-memory lookup
- **Q&A**: 2-5 seconds (GPT-4 dependent)
- **Limits**: RAM-bound (~1GB per 100K chunks)

## Future Enhancements

```python
# Persistent storage
class DatabaseStorage:
    def __init__(self):
        self.db = SQLAlchemy(DATABASE_URL)
        self.vector_db = PineconeClient()

# Advanced chunking
def chunk_by_semantic_boundaries(text):
    # Sentence transformers for topic detection
    # Sliding window with overlap
```

## Security & Monitoring

**Current:**
- Environment variables for API keys
- Input validation and error handling
- Health checks and basic metrics

**Production:**
- JWT authentication
- Rate limiting per user
- Structured logging and metrics

## Deployment

```bash
# Development
python main.py

# Docker
docker-compose up

# Production: Kubernetes with replicas
```

---

*Pragmatic architecture balancing 24h constraints with production practices*
