import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv


class GroundNewsAgent:
    """Agent for fetching news from Ground News API."""
    def __init__(self):
        self.name = "Ground News Agent"
        dotenv_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        self.api_key = os.getenv("GROUNDNEWS_API_KEY")

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from Ground News API."""
        if not self.api_key:
            print("Error: GROUNDNEWS_API_KEY not found in .env file.")
            return []
        articles = []
        articles.extend(fetch_groundnews_articles())
        articles.extend(fetch_groundnews_trending())
        articles.extend(fetch_groundnews_balanced())
        return articles


def fetch_groundnews_articles() -> List[Dict[str, Any]]:
    """
    Fetches aviation news from Ground News API.
    Ground News is a news aggregator that provides balanced coverage and fact-checking.
    """
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    GROUNDNEWS_API_KEY = os.getenv("GROUNDNEWS_API_KEY")
    if not GROUNDNEWS_API_KEY:
        print("Error: GROUNDNEWS_API_KEY not found in .env file.")
        return []

    # Ground News API endpoint for search
    url = "https://api.ground.news/search"
    
    headers = {
        "Authorization": f"Bearer {GROUNDNEWS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "query": "aviation OR airline OR aircraft",
        "language": "en",
        "pageSize": 20,
        "sortBy": "date"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if data.get("status") == "success" and data.get("articles"):
            for item in data.get("articles", []):
                article = {
                    "id": str(uuid.uuid4()),
                    "title": item.get("title"),
                    "date": item.get("publishedAt", datetime.now().isoformat()),
                    "body": item.get("description", ""),
                    "link": item.get("url"),
                    "source": f"{item.get('source', {}).get('name', 'Ground News')}",
                    "status": "new",
                    "bias": item.get("bias", "unknown"),
                    "factuality": item.get("factuality", "unknown")
                }
                
                # Ensure we have a title and a link before adding
                if article["title"] and article["link"]:
                    articles.append(article)
                    
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Ground News: {e}")
        return []
    except ValueError:
        print("Error: Could not decode JSON response from Ground News")
        return []


def fetch_groundnews_trending() -> List[Dict[str, Any]]:
    """
    Fetches trending aviation news from Ground News.
    """
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    GROUNDNEWS_API_KEY = os.getenv("GROUNDNEWS_API_KEY")
    if not GROUNDNEWS_API_KEY:
        print("Error: GROUNDNEWS_API_KEY not found in .env file.")
        return []

    # Ground News API endpoint for trending news
    url = "https://api.ground.news/trending"
    
    headers = {
        "Authorization": f"Bearer {GROUNDNEWS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "category": "business",  # Aviation news often falls under business
        "language": "en",
        "pageSize": 15
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if data.get("status") == "success" and data.get("articles"):
            for item in data.get("articles", []):
                # Filter for aviation-related content
                title = item.get("title", "").lower()
                description = item.get("description", "").lower()
                
                aviation_keywords = ["aviation", "airline", "aircraft", "airplane", "airport", "pilot", "flight"]
                if any(keyword in title or keyword in description for keyword in aviation_keywords):
                    article = {
                        "id": str(uuid.uuid4()),
                        "title": item.get("title"),
                        "date": item.get("publishedAt", datetime.now().isoformat()),
                        "body": item.get("description", ""),
                        "link": item.get("url"),
                        "source": f"{item.get('source', {}).get('name', 'Ground News')} (Trending)",
                        "status": "new",
                        "bias": item.get("bias", "unknown"),
                        "factuality": item.get("factuality", "unknown")
                    }
                    
                    if article["title"] and article["link"]:
                        articles.append(article)
                        
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trending news from Ground News: {e}")
        return []
    except ValueError:
        print("Error: Could not decode JSON response from Ground News")
        return []


def fetch_groundnews_balanced() -> List[Dict[str, Any]]:
    """
    Fetches balanced aviation news from Ground News, ensuring diverse perspectives.
    """
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    GROUNDNEWS_API_KEY = os.getenv("GROUNDNEWS_API_KEY")
    if not GROUNDNEWS_API_KEY:
        print("Error: GROUNDNEWS_API_KEY not found in .env file.")
        return []

    # Ground News API endpoint for balanced news
    url = "https://api.ground.news/balanced"
    
    headers = {
        "Authorization": f"Bearer {GROUNDNEWS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "query": "aviation OR airline OR aircraft",
        "language": "en",
        "pageSize": 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if data.get("status") == "success" and data.get("articles"):
            for item in data.get("articles", []):
                article = {
                    "id": str(uuid.uuid4()),
                    "title": item.get("title"),
                    "date": item.get("publishedAt", datetime.now().isoformat()),
                    "body": item.get("description", ""),
                    "link": item.get("url"),
                    "source": f"{item.get('source', {}).get('name', 'Ground News')} (Balanced)",
                    "status": "new",
                    "bias": item.get("bias", "unknown"),
                    "factuality": item.get("factuality", "unknown")
                }
                
                if article["title"] and article["link"]:
                    articles.append(article)
                    
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching balanced news from Ground News: {e}")
        return []
    except ValueError:
        print("Error: Could not decode JSON response from Ground News")
        return []
