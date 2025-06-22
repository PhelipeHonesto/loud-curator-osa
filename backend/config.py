from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Security
    SECRET_KEY: str = "your-secure-secret-key-for-dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Optional service keys - allow them to be None for local dev
    OPENAI_API_KEY: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_WEBHOOK_FIGMA_URL: Optional[str] = None
    NEWSDATA_API_KEY: Optional[str] = None
    GROUNDNEWS_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./news.db"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

def validate_environment() -> Settings:
    """
    Validates environment variables by loading them into the Settings model.
    Prints helpful messages for developers.
    """
    try:
        settings = Settings()
        if settings.SECRET_KEY == "your-secure-secret-key-for-dev":
            print("⚠️  WARNING: Using default SECRET_KEY. Set a secure SECRET_KEY for production.")
        
        # Check for optional but recommended keys for full functionality
        if not settings.OPENAI_API_KEY:
            print("⚠️  WARNING: OPENAI_API_KEY is not set. AI features will be disabled.")
        if not settings.SLACK_WEBHOOK_URL:
            print("⚠️  WARNING: SLACK_WEBHOOK_URL is not set. Slack posting will be disabled.")

        print("✅ Environment validation passed. Settings loaded.")
        return settings
    except ValidationError as e:
        print("❌ Environment validation failed. Please check your .env file or environment variables.")
        print(e)
        raise

# Global settings instance, validated on startup
settings = validate_environment() 