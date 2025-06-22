import asyncio
import logging
import time
import json
from typing import List, Dict, Any
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Correctly import agent instances, not modules
from backend.agents.aviation_pages_reader import aviation_reader_agent
from backend.agents.newsdata_agent import newsdata_agent
from backend.agents.rss_agent import rss_agent
from backend.agents.scoring_engine import scoring_engine
from backend.agents.headline_remixer import headline_remixer

from backend.database_sqlite import (
    Article,
    ArticleCreate,
    ArticleUpdate,
    ArticleInDB,
    SessionLocal,
    Setting,
    SettingCreate,
    SettingSchema,
    init_db,
)
from backend.logging_config import setup_logging
from backend.middleware import LoggingMiddleware
from backend.config import settings

# --- Basic Setup ---
setup_logging()
logger = logging.getLogger(__name__)

# --- Database Setup ---
def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Application Setup ---
app = FastAPI(title="Loud Curator API", version="1.0.0")

# --- Middleware ---
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def run_ingestion():
    """Run the news ingestion process."""
    logger.info("Starting news ingestion run...")
    try:
        start_time = time.time()
        sources = {
            "Aviation Pages": aviation_reader_agent,
            "NewsData": newsdata_agent,
            "RSS Feeds": rss_agent,
        }

        async def fetch_from_source(name, agent):
            try:
                return await agent.fetch_articles()
            except Exception as e:
                logger.error(f"Failed to fetch from {name}: {e}", exc_info=True)
                return []

        tasks = [fetch_from_source(name, agent) for name, agent in sources.items()]
        results = await asyncio.gather(*tasks)
        
        all_articles: List[Dict[str, Any]] = [article for result in results for article in result]

        if not all_articles:
            logger.warning("No new articles fetched from any source.")
            return

        scoring_tasks = [scoring_engine.score_article(article) for article in all_articles]
        scored_results = await asyncio.gather(*scoring_tasks, return_exceptions=True)

        processed_articles: List[Dict[str, Any]] = []
        for article_data, scored_data in zip(all_articles, scored_results):
            if isinstance(scored_data, dict):
                article_data.update(scored_data)
            else:
                logger.error(f"Scoring failed for '{article_data.get('title')}': {scored_data}", exc_info=True)
                article_data.update(scoring_engine._default_scores())
            
            try:
                if isinstance(article_data.get("date"), str):
                    article_data["date"] = datetime.fromisoformat(article_data["date"].replace("Z", "+00:00"))
                
                # Use Pydantic model for validation before adding to list
                validated_article = ArticleCreate(**article_data)
                processed_articles.append(validated_article.dict())
            except Exception as e:
                logger.error(f"Model validation failed for '{article_data.get('title')}': {e}", exc_info=True)

        if processed_articles:
            try:
                with SessionLocal() as db:
                    # Use add_all for SQLAlchemy ORM objects
                    db.add_all([Article(**article) for article in processed_articles])
                    db.commit()
                logger.info(f"Successfully saved {len(processed_articles)} articles.")
            except Exception as e:
                logger.error(f"Database save failed: {e}", exc_info=True)

        end_time = time.time()
        logger.info(f"News ingestion completed in {end_time - start_time:.2f} seconds")

    except Exception as e:
        logger.error(f"An error occurred during the ingestion process: {e}", exc_info=True)


# --- API Endpoints ---
@app.get("/api/v1/articles", response_model=List[ArticleInDB])
def get_articles(
    status: str = "draft",
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Retrieve articles with optional status filtering."""
    if status == "all":
        query = db.query(Article)
    else:
        query = db.query(Article).filter(Article.status == status)
    return query.order_by(Article.date.desc()).offset(offset).limit(limit).all()


@app.put("/api/v1/articles/{article_id}", response_model=ArticleInDB)
def update_article(
    article_id: int, article_update: ArticleUpdate, db: Session = Depends(get_db)
):
    """Update an article's status."""
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = article_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_article, key, value)

    db.commit()
    db.refresh(db_article)
    return db_article


@app.delete("/api/v1/articles/{article_id}", status_code=204)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Delete an article."""
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if db_article:
        db.delete(db_article)
        db.commit()


@app.post("/api/v1/articles/{article_id}/remix", response_model=List[str])
async def remix_headline(article_id: int, db: Session = Depends(get_db)):
    """Remix an article's headline."""
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    try:
        # Ensure title and body are strings
        title = str(db_article.title) if db_article.title is not None else ""
        body = str(db_article.body) if db_article.body is not None else ""
        return await headline_remixer.remix_headline(
            title=title,
            body=body
        )
    except Exception as e:
        logger.error(f"Failed to remix headline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to remix headline")


@app.get("/api/v1/settings", response_model=List[SettingSchema])
def get_settings_api(db: Session = Depends(get_db)):
    """Retrieve all settings."""
    return db.query(Setting).all()


@app.post("/api/v1/settings", response_model=SettingSchema)
def create_or_update_setting(
    setting: SettingCreate, db: Session = Depends(get_db)
):
    """Create or update a setting."""
    db_setting = db.query(Setting).filter(Setting.key == setting.key).first()
    if db_setting:
        # If setting exists, update its value
        db_setting.value = setting.value
    else:
        # If setting does not exist, create a new one
        db_setting = Setting(**setting.dict())
        db.add(db_setting)
    
    db.commit()
    db.refresh(db_setting)
    return db_setting


# --- Application Lifecycle ---
@app.on_event("startup")
async def startup_event():
    """Initialize database and run ingestion once on startup."""
    logger.info("Starting up Loud Curator API...")
    init_db()
    # Run ingestion once on startup
    asyncio.create_task(run_ingestion())
    logger.info("Application startup complete.")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event (no scheduler to stop)."""
    logger.info("Shutting down Loud Curator API...")
    logger.info("Loud Curator API shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
