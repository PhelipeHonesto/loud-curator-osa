import asyncio
import logging
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import feedparser
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSAgent:
    """Agent for fetching and parsing news from multiple RSS feeds."""

    DEFAULT_FEEDS = {
        "Aviation Week": "https://aviationweek.com/rss.xml",
        "Flight Global": "https://www.flightglobal.com/rss",
        "AIN Online": "https://www.ainonline.com/rss.xml",
        "Simple Flying": "https://simpleflying.com/feed/",
    }

    def __init__(self, feed_configs: Optional[Dict[str, str]] = None):
        self.feeds = feed_configs or self.DEFAULT_FEEDS
        self.user_agent = "LoudCurator/1.0"

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch and parse articles from all configured RSS feeds concurrently."""
        async with httpx.AsyncClient(
            headers={"User-Agent": self.user_agent}, follow_redirects=True
        ) as client:
            tasks = [
                self._fetch_one_feed(client, source_name, url)
                for source_name, url in self.feeds.items()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error fetching RSS feed: {result}", exc_info=True)
        
        logger.info(f"Total RSS articles fetched: {len(all_articles)}")
        return all_articles

    async def _fetch_one_feed(self, client: httpx.AsyncClient, source_name: str, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed."""
        try:
            response = await client.get(url, timeout=15.0)
            response.raise_for_status()
            
            feed_content = response.text
            parsed_feed = feedparser.parse(feed_content)

            if parsed_feed.bozo:
                bozo_exception = parsed_feed.bozo_exception
                logger.warning(f"Feed at {url} is not well-formed: {bozo_exception}")

            return [
                self._parse_entry(entry, source_name, url)
                for entry in parsed_feed.entries[:20] # Limit to 20 entries per feed
            ]

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.request.url}")
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing feed {url}: {e}", exc_info=True)
        
        return []

    def _parse_entry(self, entry: Dict[str, Any], source_name: str, feed_url: str) -> Dict[str, Any]:
        """Parse a single feed entry into a standardized article dictionary."""
        title = self._get_field_as_str(entry, "title")
        link = self._get_field_as_str(entry, "link")
        
        published_date = self._parse_date(entry)
        content = self._extract_content(entry)

        return {
            "id": str(uuid.uuid4()),
            "title": self._clean_text(title),
            "date": published_date.isoformat(),
            "body": self._clean_text(content),
            "link": link,
            "source": source_name,
            "status": "new",
            "feed_url": feed_url,
            "author": self._get_field_as_str(entry, "author"),
        }

    def _get_field_as_str(self, entry: Dict[str, Any], field: str) -> str:
        """Safely retrieve a field from an entry as a string."""
        value = entry.get(field, "")
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
             return value.get('value', '')
        if isinstance(value, list) and value:
            return str(value[0])
        return str(value) if value is not None else ""

    def _parse_date(self, entry: Dict[str, Any]) -> datetime:
        """Parse the publication date from an entry, with fallbacks."""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        for field in date_fields:
            if field in entry and entry[field]:
                try:
                    return datetime(*entry[field][:6])
                except (ValueError, TypeError):
                    continue
        return datetime.now()

    def _extract_content(self, entry: Dict[str, Any]) -> str:
        """Extract and clean main content from an entry."""
        content_fields = ['content', 'summary', 'description']
        for field in content_fields:
            if field in entry:
                value = entry[field]
                if isinstance(value, list) and value:
                    return value[0].get('value', '')
                if isinstance(value, str):
                    return value
        return ""

    def _clean_text(self, text: str) -> str:
        """Remove HTML tags and normalize whitespace."""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

# Singleton instance for the application to use
rss_agent = RSSAgent() 