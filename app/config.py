from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "JSON2Prompt API"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database settings (if needed)
    DATABASE_URL: str = ""
    
    # API settings
    API_KEY: str = ""
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
