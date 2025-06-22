from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Pydantic will automatically read from an .env file or system environment variables.
    """
    # --- Core Security ---
    SECRET_KEY: str = "your-secure-secret-key-for-dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # --- Service API Keys ---
    OPENAI_API_KEY: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_WEBHOOK_FIGMA_URL: Optional[str] = None
    NEWSDATA_API_KEY: Optional[str] = None
    GROUNDNEWS_API_KEY: Optional[str] = None

    # --- CORS ---
    # A list of allowed origins. Use ["*"] to allow all.
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://loud-curator-app.onrender.com"
    ]

    # --- Rate Limiting ---
    RATE_LIMIT_ENABLED: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./news.db"
    
    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # Pydantic model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False, # Allows env vars to be uppercase, e.g. SECRET_KEY
        extra='ignore' # Ignores extra fields from the env file
    )

# Create a single, validated settings instance for the application to use
settings = Settings()