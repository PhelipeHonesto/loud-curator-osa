class Settings:
    SECRET_KEY = "dev"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    OPENAI_API_KEY = None
    SLACK_WEBHOOK_URL = None
    SLACK_WEBHOOK_FIGMA_URL = None
    NEWSDATA_API_KEY = None
    GROUNDNEWS_API_KEY = None
    CORS_ORIGINS = ["*"]
    RATE_LIMIT_ENABLED = False
    DATABASE_URL = "sqlite:///./news.db"
    LOG_LEVEL = "INFO"

settings = Settings()
