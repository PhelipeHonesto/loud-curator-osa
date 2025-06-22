from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    slack_webhook_url: str
    slack_webhook_figma_url: str = ""
    newsdata_api_key: str = ""
    groundnews_api_key: str = ""
    secret_key: str
    cors_origins: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()