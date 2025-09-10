from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AI JSON Prompt Generator API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database settings - PostgreSQL (Neon)
    DATABASE_URL: str = "postgresql://neondb_owner:password@host.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    def get_database_url(self) -> str:
        """Get PostgreSQL database URL from environment variables"""
        # Always use environment variable for database connection
        # Format: postgresql://neondb_owner:password@ep-host.neon.tech/neondb?sslmode=require&channel_binding=require
        database_url = os.environ.get('DATABASE_URL', self.DATABASE_URL)
        
        # Ensure it's a PostgreSQL URL
        if not database_url.startswith('postgresql://'):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string starting with 'postgresql://'")
        
        return database_url
    
    # LLM Provider settings
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis settings for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    # Rate limiting - Daily limits
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Anonymous user limits (IP-based)
    ANONYMOUS_DAILY_REQUESTS: int = 10
    ANONYMOUS_DAILY_TOKENS: int = 50000
    ANONYMOUS_MAX_TOKENS_PER_REQUEST: int = 5000
    
    # Registered user limits
    REGISTERED_DAILY_REQUESTS: int = 50
    REGISTERED_DAILY_TOKENS: int = 200000
    REGISTERED_MAX_TOKENS_PER_REQUEST: int = 10000
    
    # Token usage warnings
    WARNING_THRESHOLD: float = 0.8
    HARD_STOP_THRESHOLD: float = 1.0
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
