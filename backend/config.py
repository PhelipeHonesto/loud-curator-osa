from pydantic import field_validator, ConfigDict
from typing import Optional
import os

# Import BaseSettings with explicit fallback
try:
    from pydantic_settings import BaseSettings
    BaseSettingsType = BaseSettings
except ImportError:
    from pydantic import BaseSettings
    BaseSettingsType = BaseSettings


class Settings(BaseSettingsType):
    """Application settings with environment variable validation."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    newsdata_api_key: Optional[str] = None
    groundnews_api_key: Optional[str] = None
    
    # Slack Integration
    slack_webhook_url: Optional[str] = None
    slack_webhook_figma_url: Optional[str] = None
    
    # Security
    secret_key: str = "supersecretkey"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week
    
    # Database
    database_url: str = "sqlite:///./news.db"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    # CORS
    allowed_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY is required for AI features")
        return v
    
    @field_validator('slack_webhook_url')
    @classmethod
    def validate_slack_webhook(cls, v):
        if not v:
            raise ValueError("SLACK_WEBHOOK_URL is required for Slack posting")
        return v
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v):
        if v == "supersecretkey":
            print("⚠️  WARNING: Using default SECRET_KEY. Set a secure SECRET_KEY for production.")
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


def validate_environment():
    """Validate all required environment variables are set."""
    try:
        settings = Settings()
        print("✅ Environment validation passed")
        return settings
    except ValueError as e:
        print(f"❌ Environment validation failed: {e}")
        print("\nRequired environment variables:")
        print("- OPENAI_API_KEY: Your OpenAI API key")
        print("- SLACK_WEBHOOK_URL: Your Slack webhook URL")
        print("- SLACK_WEBHOOK_FIGMA_URL: Your Figma Slack webhook URL (optional)")
        print("- NEWSDATA_API_KEY: Your NewsData.io API key (optional)")
        print("- GROUNDNEWS_API_KEY: Your Ground News API key (optional)")
        print("- SECRET_KEY: A secure secret key for JWT tokens")
        raise


# Global settings instance
settings = validate_environment() 