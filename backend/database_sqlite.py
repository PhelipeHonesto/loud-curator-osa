import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./news.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy Models ---
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    body = Column(Text)
    link = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="draft")
    score_relevance = Column(Integer, default=50)
    score_vibe = Column(Integer, default=50)
    score_viral = Column(Integer, default=50)
    target_channels = Column(JSON, default=list)
    priority = Column(String, default="low")
    auto_post = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)

# --- Pydantic Schemas ---
class ArticleBase(BaseModel):
    title: str
    link: str
    source: str
    date: datetime
    body: Optional[str] = None

class ArticleCreate(ArticleBase):
    score_relevance: int = 50
    score_vibe: int = 50
    score_viral: int = 50
    target_channels: List[str] = []
    priority: str = "low"
    auto_post: bool = False

class ArticleUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

class ArticleInDB(ArticleBase):
    id: int
    status: str
    score_relevance: int
    score_vibe: int
    score_viral: int
    target_channels: List[str]
    priority: str
    auto_post: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class SettingBase(BaseModel):
    key: str
    value: Dict[str, Any]

class SettingCreate(SettingBase):
    pass

class SettingSchema(SettingBase):
    id: int
    class Config:
        orm_mode = True

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)

if __name__ == "__main__":
    init_db() 
