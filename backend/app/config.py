import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Virality AI Pre-Flight Engine"
    API_V1_PREFIX: str = "/api/v1"
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_PERCEPTION_MODEL: str = os.getenv("GEMINI_PERCEPTION_MODEL", "gemini-2.5-flash")
    GEMINI_SYNTHESIS_MODEL: str = os.getenv("GEMINI_SYNTHESIS_MODEL", "gemini-2.5-pro")
    
    # Tiger Data / PostgreSQL connection
    # Standard format: postgresql+asyncpg://tsdbadmin:password@host.tigerdata.cloud:5432/virality_db?ssl=require
    TIGER_DATA_DATABASE_URL: Optional[str] = os.getenv(
        "TIGER_DATA_DATABASE_URL", 
        os.getenv("DATABASE_URL", "")
    )
    
    # JWT Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "innohacks-virality-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Upload folder
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    
    class Config:
        env_file = ".env"
        extra = "allow"

# Fallback without pydantic_settings if not installed
try:
    settings = Settings()
except Exception:
    class BasicSettings:
        PROJECT_NAME = "Virality AI Pre-Flight Engine"
        API_V1_PREFIX = "/api/v1"
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        GEMINI_PERCEPTION_MODEL = os.getenv("GEMINI_PERCEPTION_MODEL", "gemini-2.5-flash")
        GEMINI_SYNTHESIS_MODEL = os.getenv("GEMINI_SYNTHESIS_MODEL", "gemini-2.5-pro")
        TIGER_DATA_DATABASE_URL = os.getenv("TIGER_DATA_DATABASE_URL", os.getenv("DATABASE_URL", ""))
        JWT_SECRET = os.getenv("JWT_SECRET", "innohacks-virality-secret-key-2026")
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
        UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    settings = BasicSettings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
