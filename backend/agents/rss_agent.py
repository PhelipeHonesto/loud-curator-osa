import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import feedparser
import requests
from urllib.parse import urlparse
import re

# Common aviation and news RSS feeds
DEFAULT_RSS_FEEDS = {
    "Aviation Week": "https://aviationweek.com/rss.xml",
    "Flight Global": "https://www.flightglobal.com/rss",
    "AIN Online": "https://www.ainonline.com/rss.xml",
    "Aviation International News": "https://www.ainonline.com/rss.xml",
    "Simple Flying": "https://simpleflying.com/feed/",
    "The Points Guy": "https://thepointsguy.com/feed/",
    "Cranky Flier": "https://crankyflier.com/feed/",
    "Aviation Safety Network": "https://aviation-safety.net/rss/rss.php",
    "Flying Magazine": "https://www.flyingmag.com/feed/",
    "Pilot Magazine": "https://www.pilotweb.aero/rss.xml"
}

class RSSAgent:
    """Agent for fetching news from multiple RSS feeds."""
    def __init__(self, feed_configs: Optional[Dict[str, str]] = None):
        self.feed_configs = feed_configs or DEFAULT_RSS_FEEDS

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from all configured RSS feeds."""
        return fetch_multiple_rss_feeds(self.feed_configs)


def fetch_rss_feed(feed_url: str, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches articles from a single RSS feed.
    
    Args:
        feed_url: URL of the RSS feed
        source_name: Custom name for the source (optional)
    
    Returns:
        List of article dictionaries
    """
    try:
        # Parse the RSS feed
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"Warning: RSS feed {feed_url} has parsing issues")
        
        articles = []
        
        for entry in feed.entries[:20]:  # Limit to 20 articles per feed
            # Extract and clean the content
            content = extract_content(entry)
            
            # Parse the date
            published_date = parse_date(entry)
            
            # Create article object
            article = {
                "id": str(uuid.uuid4()),
                "title": clean_text(entry.get('title', '')),
                "date": published_date.isoformat(),
                "body": content,
                "link": entry.get('link', ''),
                "source": source_name or feed.feed.get('title', 'RSS Feed'),
                "status": "new",
                "feed_url": feed_url,
                "author": entry.get('author', ''),
                "category": extract_categories(entry)
            }
            
            # Only add articles with valid title and link
            if article["title"] and article["link"]:
                articles.append(article)
        
        print(f"Fetched {len(articles)} articles from {source_name or feed_url}")
        return articles
        
    except Exception as e:
        print(f"Error fetching RSS feed {feed_url}: {e}")
        return []


def fetch_multiple_rss_feeds(feed_configs: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """
    Fetches articles from multiple RSS feeds.
    
    Args:
        feed_configs: Dictionary of source_name -> feed_url mappings
    
    Returns:
        Combined list of articles from all feeds
    """
    if feed_configs is None:
        feed_configs = DEFAULT_RSS_FEEDS
    
    all_articles = []
    
    for source_name, feed_url in feed_configs.items():
        try:
            articles = fetch_rss_feed(feed_url, source_name)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error processing RSS feed {source_name}: {e}")
            continue
    
    print(f"Total RSS articles fetched: {len(all_articles)}")
    return all_articles


def fetch_custom_rss_feeds(feed_urls: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches articles from a list of custom RSS feed URLs.
    
    Args:
        feed_urls: List of RSS feed URLs
    
    Returns:
        List of articles from all feeds
    """
    all_articles = []
    
    for feed_url in feed_urls:
        try:
            # Extract domain name as source
            domain = urlparse(feed_url).netloc
            source_name = domain.replace('www.', '').replace('.com', '').title()
            
            articles = fetch_rss_feed(feed_url, source_name)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error processing custom RSS feed {feed_url}: {e}")
            continue
    
    return all_articles


def extract_content(entry) -> str:
    """
    Extracts and cleans content from an RSS entry.
    """
    # Try different content fields
    content_fields = ['content', 'summary', 'description']
    
    for field in content_fields:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            elif isinstance(content, str):
                content = content
            else:
                content = str(content) if content else ''
            
            if content:
                # Remove HTML tags
                content = re.sub(r'<[^>]+>', '', content)
                # Clean up whitespace
                content = re.sub(r'\s+', ' ', content).strip()
                return content[:1000]  # Limit content length
    
    return ""


def parse_date(entry) -> datetime:
    """
    Parses the publication date from an RSS entry.
    """
    date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
    
    for field in date_fields:
        if hasattr(entry, field):
            parsed_date = getattr(entry, field)
            if parsed_date:
                try:
                    return datetime(*parsed_date[:6])
                except (ValueError, TypeError):
                    continue
    
    # Fallback to current time
    return datetime.now()


def clean_text(text: str) -> str:
    """
    Cleans and normalizes text content.
    """
    if not text:
        return ""
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_categories(entry) -> List[str]:
    """
    Extracts categories/tags from an RSS entry.
    """
    categories = []
    
    # Try different category fields
    if hasattr(entry, 'tags') and entry.tags:
        categories.extend([tag.term for tag in entry.tags])
    
    if hasattr(entry, 'category') and entry.category:
        categories.append(entry.category)
    
    return categories


def fetch_aviation_rss_feeds() -> List[Dict[str, Any]]:
    """
    Fetches articles from aviation-specific RSS feeds.
    """
    aviation_feeds = {
        "Aviation Week": "https://aviationweek.com/rss.xml",
        "Flight Global": "https://www.flightglobal.com/rss",
        "Simple Flying": "https://simpleflying.com/feed/",
        "Flying Magazine": "https://www.flyingmag.com/feed/"
    }
    
    return fetch_multiple_rss_feeds(aviation_feeds)


def fetch_business_rss_feeds() -> List[Dict[str, Any]]:
    """
    Fetches articles from business news RSS feeds that might contain aviation content.
    """
    business_feeds = {
        "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
        "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
        "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/"
    }
    
    return fetch_multiple_rss_feeds(business_feeds)


def validate_rss_feed(feed_url: str) -> bool:
    """
    Validates if a URL is a valid RSS feed.
    
    Args:
        feed_url: URL to validate
    
    Returns:
        True if valid RSS feed, False otherwise
    """
    try:
        feed = feedparser.parse(feed_url)
        return len(feed.entries) > 0
    except Exception:
        return False


def get_feed_info(feed_url: str) -> Dict[str, Any]:
    """
    Gets information about an RSS feed.
    
    Args:
        feed_url: URL of the RSS feed
    
    Returns:
        Dictionary with feed information
    """
    try:
        feed = feedparser.parse(feed_url)
        
        return {
            "title": feed.feed.get('title', ''),
            "description": feed.feed.get('description', ''),
            "link": feed.feed.get('link', ''),
            "language": feed.feed.get('language', ''),
            "entry_count": len(feed.entries),
            "last_updated": feed.feed.get('updated', ''),
            "is_valid": len(feed.entries) > 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "is_valid": False
        } 