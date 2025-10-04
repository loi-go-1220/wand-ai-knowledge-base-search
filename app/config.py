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
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30  # seconds
    
    # Monitoring Settings
    ENABLE_METRICS: bool = True
    METRICS_RETENTION_HOURS: int = 24
    
    def validate_settings(self) -> bool:
        """Validate all settings and return True if valid"""
        issues = []
        
        if not self.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY not set")
        
        if self.MAX_CHUNK_SIZE < 100:
            issues.append("MAX_CHUNK_SIZE too small (minimum 100)")
        
        if self.MAX_FILE_SIZE < 1024:  # 1KB minimum
            issues.append("MAX_FILE_SIZE too small (minimum 1KB)")
        
        if self.SIMILARITY_THRESHOLD < 0 or self.SIMILARITY_THRESHOLD > 1:
            issues.append("SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if issues:
            print("⚠️  Configuration Issues:")
            for issue in issues:
                print(f"   • {issue}")
            return False
        
        return True
    
    def get_summary(self) -> dict:
        """Get configuration summary for monitoring"""
        return {
            "openai_configured": bool(self.OPENAI_API_KEY),
            "max_chunk_size": self.MAX_CHUNK_SIZE,
            "max_file_size_mb": self.MAX_FILE_SIZE // (1024 * 1024),
            "embedding_model": self.OPENAI_EMBEDDING_MODEL,
            "chat_model": self.OPENAI_CHAT_MODEL,
            "debug_mode": self.DEBUG
        }

# Global settings instance
settings = Settings()

# Validation
if not settings.validate_settings():
    print("⚠️  Some configuration issues detected. System may not work properly.")
else:
    print("✅ Configuration validated successfully")
