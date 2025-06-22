import asyncio
import logging
import time
from typing import List, Dict, Any, Optional

from agents.aviation_pages_reader import AviationPagesReader
from agents.newsdata_agent import NewsDataAgent
from agents.groundnews_agent import GroundNewsAgent
from agents.institutional_reader import InstitutionalReader
from agents.rss_agent import RSSAgent
from database_sqlite import init_database, get_database
from logging_config import setup_logging
from config import settings

setup_logging(enable_file=False)
logger = logging.getLogger(__name__)

db = init_database()

aviation_reader = AviationPagesReader()
newsdata_agent = NewsDataAgent()
groundnews_agent = GroundNewsAgent()
institutional_reader = InstitutionalReader()
rss_agent = RSSAgent()

def ingest_news() -> Dict[str, Any]:
    return asyncio.run(run_ingestion())

async def run_ingestion() -> Dict[str, Any]:
    logger.info("Starting news ingestion run...")
    start_time = time.time()
    all_new_articles: List[Dict[str, Any]] = []

    # RSS Agent
    rss_articles = await rss_agent.fetch_articles()
    all_new_articles.extend(rss_articles)

    if settings.NEWSDATA_API_KEY:
        newsdata_articles = await newsdata_agent.fetch_articles()
        all_new_articles.extend(newsdata_articles)

    if settings.GROUNDNEWS_API_KEY:
        groundnews_articles = await groundnews_agent.fetch_articles()
        all_new_articles.extend(groundnews_articles)

    institutional_articles = await institutional_reader.fetch_articles()
    all_new_articles.extend(institutional_articles)

    aviation_articles = await aviation_reader.fetch_articles()
    all_new_articles.extend(aviation_articles)

    if all_new_articles:
        from agents.scoring_engine import score_and_route_article

        unique_articles = deduplicate_articles(all_new_articles)
        for article in unique_articles:
            try:
                result = score_and_route_article(article)
                article.update(result)
            except Exception:
                article.update({
                    'score_relevance': 50,
                    'score_vibe': 50,
                    'score_viral': 50,
                    'target_channels': [],
                    'auto_post': False,
                    'priority': 'low',
                })
        db.save_all_articles(unique_articles)

    elapsed_time = time.time() - start_time
    logger.info("News ingestion completed in %.2f seconds", elapsed_time)
    return {"message": "Successfully ingested", "count": len(all_new_articles)}


def deduplicate_articles(new_articles: List[Dict[str, Any]], existing_articles: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    if not new_articles:
        return []
    existing_articles = existing_articles or []
    unique_articles: List[Dict[str, Any]] = []
    seen_urls = {a.get("link", "").strip() for a in existing_articles}
    seen_titles = {a.get("title", "").strip().lower() for a in existing_articles}

    for article in new_articles:
        url = article.get("link", "").strip()
        title = article.get("title", "").strip().lower()
        if url in seen_urls:
            continue
        if any(title_similarity(title, t) >= 0.8 for t in seen_titles):
            continue
        unique_articles.append(article)
        seen_urls.add(url)
        seen_titles.add(title)
    return unique_articles


def title_similarity(title1: str, title2: str) -> float:
    words1 = set(title1.split())
    words2 = set(title2.split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)
