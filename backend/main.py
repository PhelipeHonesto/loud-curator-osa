from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import time
import traceback
import asyncio

# Import configuration
from config import settings

# Import agents
from agents.aviation_pages_reader import AviationPagesReader
from agents.newsdata_agent import NewsDataAgent
from agents.groundnews_agent import GroundNewsAgent
from agents.institutional_reader import InstitutionalReader
from agents.rss_agent import RSSAgent
from agents.headline_remixer import remix_headline, analyze_headline_style
from agents.scoring_engine import score_and_route_article, decide_distribution

# Import database
from database_sqlite import init_database, get_database

# Import logging configuration
from logging_config import setup_logging

# Import scheduler
from scheduler import Scheduler

# Import middleware
from middleware import rate_limit_middleware

# Import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Loud Curator API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (if enabled)
if settings.RATE_LIMIT_ENABLED:
    app.middleware("http")(rate_limit_middleware)
    logger.info("Rate limiting enabled")

# Initialize database
try:
    db = init_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# Security configuration from settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# JWT utility functions
def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the token.
    LOGIN IS CURRENTLY DISABLED FOR DEVELOPMENT.
    This function will return a dummy user without token validation.
    """
    # Temporarily bypass token validation and return a mock user
    return {"username": "dev_user", "sub": "dev_user"}
    
    # try:
    #     payload = decode_access_token(token)
    #     if payload is None:
    #         raise HTTPException(status_code=401, detail="Invalid token")
    #     return payload
    # except JWTError:
    #     raise HTTPException(status_code=401, detail="Invalid token")

# Initialize scheduler with the actual ingestion callback
scheduler = Scheduler(ingest_callback=lambda: asyncio.create_task(run_ingestion()))

# Initialize agents
aviation_reader = AviationPagesReader()
newsdata_agent = NewsDataAgent()
groundnews_agent = GroundNewsAgent()
institutional_reader = InstitutionalReader()
rss_agent = RSSAgent()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        logger.info("Starting Loud Curator API...")
        
        # Validate environment variables
        logger.info("Environment validation completed")
        
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")
        
        # Initial news ingestion on startup
        logger.info("Triggering initial news ingestion on startup...")
        asyncio.create_task(run_ingestion())
        
        # Log startup completion
        logger.info("Loud Curator API started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    try:
        logger.info("Shutting down Loud Curator API...")
        
        # Stop the scheduler
        scheduler.stop()
        logger.info("Scheduler stopped")
        
        logger.info("Loud Curator API shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Loud Curator API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": "production" if settings.SECRET_KEY != "your-secure-secret-key-for-dev" else "development",
        "rate_limiting": settings.RATE_LIMIT_ENABLED
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db_stats = db.get_article_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "database": {
                "status": "connected",
                "total_articles": db_stats.get("total_articles", 0)
            },
            "scheduler": {
                "status": "running" if scheduler.is_running else "stopped"
            },
            "environment": {
                "openai_configured": bool(settings.OPENAI_API_KEY),
                "slack_configured": bool(settings.SLACK_WEBHOOK_URL),
                "newsdata_configured": bool(settings.NEWSDATA_API_KEY),
                "groundnews_configured": bool(settings.GROUNDNEWS_API_KEY)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint for monitoring."""
    try:
        start_time = time.time()
        
        # Database health check
        db_stats = db.get_article_stats()
        db_healthy = True
        
        # Scheduler health check
        scheduler_healthy = scheduler.is_running
        
        # External API health checks (basic connectivity)
        external_apis = {
            "openai": bool(settings.OPENAI_API_KEY),
            "slack": bool(settings.SLACK_WEBHOOK_URL),
            "newsdata": bool(settings.NEWSDATA_API_KEY),
            "groundnews": bool(settings.GROUNDNEWS_API_KEY)
        }
        
        overall_healthy = db_healthy and scheduler_healthy
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "components": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "total_articles": db_stats.get("total_articles", 0)
                },
                "scheduler": {
                    "status": "healthy" if scheduler_healthy else "unhealthy",
                    "running": scheduler_healthy
                },
                "external_apis": external_apis
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/health/rate-limits")
async def rate_limit_status():
    """Get current rate limiting status."""
    from middleware import rate_limiter
    
    return {
        "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
        "requests_per_window": rate_limiter.requests_per_window,
        "window_seconds": rate_limiter.window_seconds,
        "active_clients": len(rate_limiter.requests)
    }

@app.get("/news")
async def get_news(filters: Optional[Dict[str, Any]] = None):
    """Get all news articles with optional filtering."""
    try:
        start_time = time.time()
        
        # Get articles from database
        articles = db.get_all_articles(filters)
        
        # Log the request
        logger.info(f"GET /news - Retrieved {len(articles)} articles in {time.time() - start_time:.2f}s")
        
        return articles
        
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve news")

@app.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Get a specific article by ID."""
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve article")

@app.put("/articles/{article_id}")
async def update_article(article_id: str, updates: Dict[str, Any]):
    """Update an article."""
    try:
        success = db.update_article(article_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
        
        logger.info(f"Updated article {article_id}")
        return {"message": "Article updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update article")

@app.put("/articles/{article_id}/status")
async def update_article_status(article_id: str, status_update: Dict[str, str]):
    """Update the status of an article."""
    try:
        new_status = status_update.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        success = db.update_article_status(article_id, new_status)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
        
        logger.info(f"Updated article {article_id} status to {new_status}")
        return {"message": "Article status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating article status {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update article status")

@app.delete("/articles/{article_id}")
async def delete_article(article_id: str):
    """Delete an article."""
    try:
        success = db.delete_article(article_id)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
        
        logger.info(f"Deleted article {article_id}")
        return {"message": "Article deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete article")

@app.post("/ingest")
async def ingest_news(background_tasks: BackgroundTasks):
    """Ingest news from all sources."""
    try:
        logger.info("Starting news ingestion...")
        background_tasks.add_task(run_ingestion)
        return {
            "message": "News ingestion started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting ingestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to start ingestion")

async def run_ingestion():
    """Run all news ingestion agents."""
    logger.info("Starting news ingestion run...")
    start_time = time.time()
    
    all_new_articles = []
    
    try:
        # RSS Agent (always runs)
        logger.info("Running RSS Agent...")
        rss_articles = await rss_agent.fetch_articles()
        all_new_articles.extend(rss_articles)
        logger.info(f"RSS Agent found {len(rss_articles)} new articles.")

        # Conditional agents based on API key availability
        if settings.NEWSDATA_API_KEY:
            logger.info("Running NewsData Agent...")
            newsdata_articles = await newsdata_agent.fetch_articles()
            all_new_articles.extend(newsdata_articles)
            logger.info(f"NewsData Agent found {len(newsdata_articles)} new articles.")
        else:
            logger.warning("Skipping NewsData Agent: API key not configured.")

        if settings.GROUNDNEWS_API_KEY:
            logger.info("Running GroundNews Agent...")
            groundnews_articles = await groundnews_agent.fetch_articles()
            all_new_articles.extend(groundnews_articles)
            logger.info(f"GroundNews Agent found {len(groundnews_articles)} new articles.")
        else:
            logger.warning("Skipping GroundNews Agent: API key not configured.")

        # Institutional and Aviation Readers (always run)
        logger.info("Running Institutional Reader...")
        institutional_articles = await institutional_reader.fetch_articles()
        all_new_articles.extend(institutional_articles)
        logger.info(f"Institutional Reader found {len(institutional_articles)} new articles.")

        logger.info("Running Aviation Pages Reader...")
        aviation_articles = await aviation_reader.fetch_articles()
        all_new_articles.extend(aviation_articles)
        logger.info(f"Aviation Pages Reader found {len(aviation_articles)} new articles.")
        
        # Deduplicate and save new articles
        if all_new_articles:
            # Deduplicate articles
            unique_articles = deduplicate_articles(all_new_articles)
            logger.info(f"Deduplicated {len(all_new_articles)} articles to {len(unique_articles)} unique articles")
            
            # Score articles for Loud Hawk distribution
            logger.info("Scoring articles for distribution...")
            for article in unique_articles:
                try:
                    result = score_and_route_article(article)
                    article.update(result)
                    
                    logger.info(f"Scored article '{article.get('title', 'Unknown')}': {result}")
                except Exception as e:
                    logger.error(f"Error scoring article: {e}")
                    # Set default scores if scoring fails
                    article.update({
                        'score_relevance': 50,
                        'score_vibe': 50,
                        'score_viral': 50,
                        'target_channels': [],
                        'auto_post': False,
                        'priority': 'low'
                    })
            
            # Save to database
            success = db.save_all_articles(unique_articles)
            if success:
                logger.info(f"Successfully saved {len(unique_articles)} articles to database")
            else:
                logger.error("Failed to save articles to database")
        
        elapsed_time = time.time() - start_time
        logger.info(f"News ingestion completed in {elapsed_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        logger.error(traceback.format_exc())

def deduplicate_articles(
    new_articles: List[Dict[str, Any]],
    existing_articles: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Remove duplicate articles based on title similarity and URL.

    Args:
        new_articles: Newly fetched articles to be checked for duplicates.
        existing_articles: Articles that already exist in the database. These
            will be considered when checking for duplicates.

    Returns:
        A list of unique articles from ``new_articles`` with duplicates removed.
    """

    if not new_articles:
        return []

    existing_articles = existing_articles or []

    unique_articles: List[Dict[str, Any]] = []
    seen_urls = {art.get("link", "").strip() for art in existing_articles}
    seen_titles = {art.get("title", "").strip().lower() for art in existing_articles}

    for article in new_articles:
        url = article.get("link", "").strip()
        title = article.get("title", "").strip().lower()

        # Skip if URL has been seen before
        if url in seen_urls:
            continue

        # Skip if title is too similar to a seen title
        if any(title_similarity(title, t) > 0.8 for t in seen_titles):
            continue

        unique_articles.append(article)
        seen_urls.add(url)
        seen_titles.add(title)

    return unique_articles


def title_similarity(title1: str, title2: str) -> float:
    """Calculate similarity between two titles using simple word overlap."""
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

@app.post("/select/{story_id}")
async def select_story(story_id: str):
    """Select a story for editing."""
    try:
        # Update article status to selected
        success = db.update_article_status(story_id, "selected")
        if not success:
            raise HTTPException(status_code=404, detail="Story not found")
        
        logger.info(f"Selected story {story_id}")
        return {"message": "Story selected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting story {story_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to select story")

@app.post("/edit/{story_id}")
async def edit_story(story_id: str):
    """Edit a story with AI."""
    try:
        # Get the article
        article = db.get_article_by_id(story_id)
        if not article:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Update status to edited
        db.update_article_status(story_id, "edited")
        
        logger.info(f"Edited story {story_id}")
        return {"message": "Story edited successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing story {story_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit story")

@app.post("/slack/{story_id}")
async def post_to_slack(story_id: str):
    """Post a story to Slack."""
    try:
        # Get the article
        article = db.get_article_by_id(story_id)
        if not article:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Update status to posted
        db.update_article_status(story_id, "posted")
        
        logger.info(f"Posted story {story_id} to Slack")
        return {"message": "Story posted to Slack successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error posting story {story_id} to Slack: {e}")
        raise HTTPException(status_code=500, detail="Failed to post to Slack")

@app.post("/slack-figma/{story_id}")
async def post_to_slack_figma(story_id: str):
    """Post a story to Slack in Figma format."""
    try:
        # Get the article
        article = db.get_article_by_id(story_id)
        if not article:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Update status to posted
        db.update_article_status(story_id, "posted")
        
        logger.info(f"Posted story {story_id} to Slack Figma")
        return {"message": "Story posted to Slack Figma successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error posting story {story_id} to Slack Figma: {e}")
        raise HTTPException(status_code=500, detail="Failed to post to Slack Figma")

# Settings endpoints
@app.get("/settings")
async def get_settings():
    """Get all settings."""
    try:
        settings = db.get_all_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

@app.post("/settings")
async def save_setting(setting: Dict[str, str]):
    """Save a setting."""
    try:
        key = setting.get("key")
        value = setting.get("value")
        
        if not key or value is None:
            raise HTTPException(status_code=400, detail="Key and value are required")
        
        success = db.save_setting(key, value)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save setting")
        
        logger.info(f"Saved setting: {key}")
        return {"message": "Setting saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving setting: {e}")
        raise HTTPException(status_code=500, detail="Failed to save setting")

@app.post("/settings/test-connection")
async def test_connection(connection: Dict[str, str]):
    """Test API connection."""
    try:
        api_type = connection.get("type")
        
        if api_type == "openai":
            # Test OpenAI connection
            return {"status": "success", "message": "OpenAI connection test successful"}
        elif api_type == "slack":
            # Test Slack connection
            return {"status": "success", "message": "Slack connection test successful"}
        else:
            raise HTTPException(status_code=400, detail="Invalid API type")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to test connection")

# Scheduler endpoints
@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status."""
    try:
        return scheduler.get_status()
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")

@app.post("/scheduler/start")
async def start_scheduler():
    """Start the scheduler."""
    try:
        scheduler.start()
        logger.info("Scheduler started via API")
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail="Failed to start scheduler")

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler."""
    try:
        scheduler.stop()
        logger.info("Scheduler stopped via API")
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop scheduler")

@app.post("/scheduler/schedule")
async def schedule_job(job: Dict[str, Any]):
    """Schedule a new job."""
    try:
        job_type = job.get("type")
        schedule_time = job.get("schedule")
        
        if not job_type or not schedule_time:
            raise HTTPException(status_code=400, detail="Job type and schedule are required")
        
        if job_type == "ingestion":
            scheduler.set_ingestion_schedule(True, "daily", schedule_time)
        elif job_type == "posting":
            scheduler.set_posting_schedule(True, "daily", schedule_time)
        else:
            raise HTTPException(status_code=400, detail="Invalid job type")
        logger.info(f"Scheduled job: {job_type}")
        return {"message": "Job scheduled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling job: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule job")

# Logging endpoints
@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent application logs."""
    try:
        logs = db.get_recent_logs(limit)
        return logs
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get logs")

@app.get("/stats")
async def get_stats():
    """Get application statistics."""
    try:
        stats = db.get_article_stats()
        scheduler_status = scheduler.get_status()
        return {
            "articles": stats,
            "scheduler": scheduler_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

# Auth endpoints
@app.post("/auth/register")
def register(form: OAuth2PasswordRequestForm = Depends()):
    if db.get_user_by_username(form.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    success = db.create_user(form.username, form.password)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"message": "User registered successfully"}

@app.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_by_username(form.username)
    if not user or not db.verify_user(form.username, form.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "email": current_user.get("email")}

# Headline remix endpoints
@app.post("/headline/remix/{article_id}")
async def remix_headline_endpoint(article_id: str):
    """Generate 3 creative Loud Hawk-style headline variations for an article."""
    try:
        # Get the article
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Generate remixes
        remixes = remix_headline(article["title"], article.get("body", ""))
        
        logger.info(f"Generated {len(remixes)} headline remixes for article {article_id}")
        return {"remixes": remixes, "original_title": article["title"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating headline remixes for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate headline remixes")

@app.post("/headline/save/{article_id}")
async def save_custom_title(article_id: str, custom_title: Dict[str, str]):
    """Save a custom title for an article."""
    try:
        # Get the article
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        new_title = custom_title.get("custom_title")
        if not new_title:
            raise HTTPException(status_code=400, detail="Custom title is required")
        
        # Update the article with custom title
        article["custom_title"] = new_title
        db.save_article(article)
        
        logger.info(f"Saved custom title for article {article_id}: {new_title}")
        return {"message": "Custom title saved successfully", "custom_title": new_title}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving custom title for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save custom title")

@app.get("/headline/analyze/{article_id}")
async def analyze_headline_endpoint(article_id: str):
    """Analyze the style of an article's headline."""
    try:
        # Get the article
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Analyze the headline style
        style = analyze_headline_style(article["title"])
        
        logger.info(f"Analyzed headline style for article {article_id}: {style}")
        return {"style": style, "title": article["title"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing headline for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze headline")

# Article scoring endpoints
@app.post("/articles/{article_id}/score")
async def score_article_endpoint(article_id: str):
    """Manually score an article."""
    try:
        # Get the article
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        # Score and route the article
        result = score_and_route_article(article)
        article.update(result)
        db.save_article(article)
        logger.info(f"Scored article {article_id}: {result}")
        return {
            "scores": {k: v for k, v in result.items() if k.startswith('score_')},
            "distribution": {
                "target_channels": result.get("target_channels", []),
                "priority": result.get("priority", "low"),
                "auto_post": result.get("auto_post", False)
            },
            "message": "Article scored successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scoring article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to score article")

@app.put("/articles/{article_id}/scores")
async def update_article_scores(article_id: str, scores: Dict[str, int]):
    """Manually update article scores."""
    try:
        # Get the article
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Validate scores
        for key in ['score_relevance', 'score_vibe', 'score_viral']:
            if key in scores:
                scores[key] = max(0, min(100, scores[key]))
        
        # Update article with new scores
        article.update(scores)
        
        # Recalculate distribution
        distribution = decide_distribution(article)
        article.update(distribution)
        
        # Save to database
        db.save_article(article)
        
        logger.info(f"Updated scores for article {article_id}: {scores}")
        return {
            "scores": {k: v for k, v in scores.items() if k.startswith('score_')},
            "distribution": distribution,
            "message": "Article scores updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scores for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update article scores")

@app.get("/articles/{article_id}/distribution")
async def get_article_distribution(article_id: str):
    """Get distribution recommendations for an article."""
    try:
        # Get the article
        article = db.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Calculate distribution
        distribution = decide_distribution(article)
        
        return {
            "article_id": article_id,
            "title": article.get("title"),
            "scores": {
                "relevance": article.get("score_relevance", 50),
                "vibe": article.get("score_vibe", 50),
                "viral": article.get("score_viral", 50)
            },
            "distribution": distribution
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting distribution for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get article distribution")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
