from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Company API (for frontend)
    COMPANY_API_URL: Optional[str] = None
    COMPANY_API_KEY: Optional[str] = None
    
    # Database Performance
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Keep-Alive
    KEEP_ALIVE_ENABLED: bool = True
    KEEP_ALIVE_INTERVAL: int = 4  # seconds
    KEEP_ALIVE_URL: Optional[str] = None  # Auto-generated if None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields

settings = Settings()
