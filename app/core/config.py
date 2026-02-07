from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Mini Social Media"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Uploads
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True

# THE CRITICAL LINE:
settings = Settings()