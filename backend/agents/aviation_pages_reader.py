import uuid
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Dict, Any
import asyncio

import requests
import re


class AviationPagesReader:
    """Reader for aviation news from various sources."""
    
    def __init__(self):
        self.name = "Aviation Pages Reader"
    
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from aviation sources."""
        articles = []
        
        # Fetch from SkyWest
        try:
            skywest_articles = fetch_skywest_news()
            articles.extend(skywest_articles)
        except Exception as e:
            print(f"Error fetching SkyWest news: {e}")
        
        return articles


def fetch_skywest_news():
    """
    Scrapes the SkyWest, Inc. press release website for news.
    """
    URL = "https://inc.skywest.com/news-and-events/press-releases/"
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Error fetching URL {URL}: {e}")
        return []

    try:
        html = response.content
        if isinstance(html, bytes):
            html = html.decode("utf-8", errors="ignore")
        pattern = re.compile(
            r'<div class="news-release-item">.*?<h4>\s*<a href="(?P<link>[^"]+)">(?P<title>[^<]+)</a>.*?'
            r'<div class="news-release-date">(?P<date>[^<]+)</div>',
            re.S,
        )

        articles = []
        count = 0
        for match in pattern.finditer(html):
            title = match.group("title").strip()
            relative_link = match.group("link")
            link = urljoin(URL, relative_link)
            date_str = match.group("date").strip()
            try:
                parsed_date = datetime.strptime(date_str, "%m/%d/%Y")
            except ValueError:
                parsed_date = datetime.now()

            articles.append(
                {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "date": parsed_date.isoformat(),
                    "body": "",
                    "link": link,
                    "source": "SkyWest, Inc.",
                    "status": "new",
                }
            )

            count += 1
            if count >= 15:
                break

        return articles
    except Exception as e:
        print(f"Error parsing SkyWest news content: {e}")
        return []
