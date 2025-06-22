from typing import List, Dict, Any, Optional

class InMemoryDB:
    def __init__(self):
        self.articles: Dict[str, Dict[str, Any]] = {}
        self.settings: Dict[str, str] = {}

    def save_all_articles(self, articles: List[Dict[str, Any]]) -> bool:
        for art in articles:
            self.articles[art['id']] = art
        return True

    def get_all_articles(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return list(self.articles.values())

    def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        return self.articles.get(article_id)

    def update_article_status(self, article_id: str, status: str) -> bool:
        if article_id in self.articles:
            self.articles[article_id]['status'] = status
            return True
        return False

    def save_article(self, article: Dict[str, Any]) -> bool:
        self.articles[article['id']] = article
        return True

    def get_article_stats(self) -> Dict[str, Any]:
        return {"total_articles": len(self.articles)}

    def migrate_from_json(self, *args, **kwargs) -> bool:
        return True


db_instance = InMemoryDB()

def init_database():
    return db_instance

def get_database():
    return db_instance
