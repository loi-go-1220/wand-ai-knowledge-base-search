"""
Configuration management
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4"
    
    # Application Settings 
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./knowledge_base.db")
    
    # Document Processing
    MAX_CHUNK_SIZE: int = 1000  # tokens
    CHUNK_OVERLAP: int = 200    # tokens
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Search Settings
    DEFAULT_SEARCH_LIMIT: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

# Global settings instance
settings = Settings()

# Validation
if not settings.OPENAI_API_KEY:
    print("⚠️  WARNING: OPENAI_API_KEY not set!")
    print("   Create .env file with your OpenAI API key")
