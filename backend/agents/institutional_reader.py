import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv


class InstitutionalReader:
    """Agent for fetching news from institutional sources via Newsdata.io API."""
    def __init__(self):
        self.name = "Institutional Reader"
        dotenv_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        self.api_key = os.getenv("NEWSDATA_API_KEY")

    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from institutional sources."""
        if not self.api_key:
            print("Error: NEWSDATA_API_KEY not found in .env file.")
            return []
        articles = []
        articles.extend(fetch_institutional_news())
        articles.extend(fetch_reuters_aviation())
        return articles


def fetch_institutional_news() -> List[Dict[str, Any]]:
    """
    Fetches news from institutional sources using Newsdata.io API.
    Focuses on major news outlets and institutional sources.
    """
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    API_KEY = os.getenv("NEWSDATA_API_KEY")
    if not API_KEY:
        print("Error: NEWSDATA_API_KEY not found in .env file.")
        return []

    # Define institutional sources to focus on
    institutional_sources = [
        "reuters", "ap", "bloomberg", "cnbc", "wsj", "ft", 
        "bbc", "cnn", "nbc", "abc", "cbs", "fox", "npr"
    ]
    
    articles = []
    
    for source in institutional_sources:
        try:
            # Fetch news from each institutional source
            url = f"https://newsdata.io/api/1/news"
            params = {
                "apikey": API_KEY,
                "q": "aviation OR airline OR aircraft",
                "language": "en",
                "domain": source,
                "size": 5  # Limit to 5 articles per source
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                for item in data.get("results", []):
                    article = {
                        "id": str(uuid.uuid4()),
                        "title": item.get("title"),
                        "date": item.get("pubDate", datetime.now().isoformat()),
                        "body": item.get("description", ""),
                        "link": item.get("link"),
                        "source": f"{item.get('source_id', 'Unknown')} (Institutional)",
                        "status": "new",
                    }
                    
                    # Ensure we have a title and a link before adding
                    if article["title"] and article["link"]:
                        articles.append(article)
                        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from {source}: {e}")
            continue
        except ValueError:
            print(f"Error: Could not decode JSON response from {source}")
            continue

    print(f"Fetched {len(articles)} articles from institutional sources.")
    return articles


def fetch_reuters_aviation() -> List[Dict[str, Any]]:
    """
    Specifically fetches aviation news from Reuters.
    """
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    API_KEY = os.getenv("NEWSDATA_API_KEY")
    if not API_KEY:
        print("Error: NEWSDATA_API_KEY not found in .env file.")
        return []

    url = f"https://newsdata.io/api/1/news"
    params = {
        "apikey": API_KEY,
        "q": "aviation OR airline OR aircraft",
        "language": "en",
        "domain": "reuters",
        "size": 10
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if data.get("status") == "success":
            for item in data.get("results", []):
                article = {
                    "id": str(uuid.uuid4()),
                    "title": item.get("title"),
                    "date": item.get("pubDate", datetime.now().isoformat()),
                    "body": item.get("description", ""),
                    "link": item.get("link"),
                    "source": "Reuters",
                    "status": "new",
                }
                
                if article["title"] and article["link"]:
                    articles.append(article)
                    
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Reuters: {e}")
        return []
    except ValueError:
        print("Error: Could not decode JSON response from Reuters")
        return []
