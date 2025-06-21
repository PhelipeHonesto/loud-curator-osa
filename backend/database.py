import json
from pathlib import Path
from typing import List, Dict, Optional

# Define the path to the news.json file relative to this file
DB_FILE = Path(__file__).parent / "news.json"

def get_all_news() -> List[Dict]:
    """Loads all news articles from the JSON database."""
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_all_news(news_list: List[Dict]):
    """Saves a list of news articles to the JSON database."""
    with open(DB_FILE, "w") as f:
        json.dump(news_list, f, indent=2)

def find_news_by_id(story_id: str) -> Optional[Dict]:
    """Finds a single news article by its ID."""
    all_news = get_all_news()
    for article in all_news:
        if article.get("id") == story_id:
            return article
    return None
