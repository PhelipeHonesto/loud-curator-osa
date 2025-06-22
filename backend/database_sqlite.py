import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import bcrypt

logger = logging.getLogger(__name__)

class SQLiteDatabase:
    """SQLite database implementation for news articles."""
    
    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create articles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        body TEXT,
                        link TEXT UNIQUE,
                        source TEXT,
                        date TEXT,
                        status TEXT DEFAULT 'new',
                        tone TEXT DEFAULT 'dry',
                        custom_title TEXT,
                        author TEXT,
                        category TEXT,
                        feed_url TEXT,
                        score_relevance INTEGER DEFAULT 50,
                        score_vibe INTEGER DEFAULT 50,
                        score_viral INTEGER DEFAULT 50,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_link ON articles(link)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_article(self, article: Dict[str, Any]) -> bool:
        """Save a single article to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO articles 
                    (id, title, body, link, source, date, status, tone, custom_title, author, category, feed_url, score_relevance, score_vibe, score_viral, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article.get('id'),
                    article.get('title'),
                    article.get('body'),
                    article.get('link'),
                    article.get('source'),
                    article.get('date'),
                    article.get('status', 'new'),
                    article.get('tone', 'dry'),
                    article.get('custom_title'),
                    article.get('author'),
                    json.dumps(article.get('category', [])),
                    article.get('feed_url'),
                    article.get('score_relevance', 50),
                    article.get('score_vibe', 50),
                    article.get('score_viral', 50),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            return False
    
    def save_all_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Save multiple articles to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for article in articles:
                    cursor.execute('''
                        INSERT OR REPLACE INTO articles 
                        (id, title, body, link, source, date, status, tone, custom_title, author, category, feed_url, score_relevance, score_vibe, score_viral, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article.get('id'),
                        article.get('title'),
                        article.get('body'),
                        article.get('link'),
                        article.get('source'),
                        article.get('date'),
                        article.get('status', 'new'),
                        article.get('tone', 'dry'),
                        article.get('custom_title'),
                        article.get('author'),
                        json.dumps(article.get('category', [])),
                        article.get('feed_url'),
                        article.get('score_relevance', 50),
                        article.get('score_vibe', 50),
                        article.get('score_viral', 50),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(articles)} articles to database")
                return True
                
        except Exception as e:
            logger.error(f"Error saving articles: {e}")
            return False
    
    def get_all_articles(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all articles with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM articles"
                params = []
                
                if filters:
                    conditions = []
                    
                    if filters.get('status'):
                        conditions.append("status = ?")
                        params.append(filters['status'])
                    
                    if filters.get('source'):
                        conditions.append("source = ?")
                        params.append(filters['source'])
                    
                    if filters.get('search'):
                        conditions.append("(title LIKE ? OR body LIKE ?)")
                        search_term = f"%{filters['search']}%"
                        params.extend([search_term, search_term])
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY date DESC, created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                articles = []
                for row in rows:
                    article = dict(row)
                    # Parse category JSON
                    if article.get('category'):
                        try:
                            article['category'] = json.loads(article['category'])
                        except:
                            article['category'] = []
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.error(f"Error getting articles: {e}")
            return []
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific article by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
                row = cursor.fetchone()
                
                if row:
                    article = dict(row)
                    if article.get('category'):
                        try:
                            article['category'] = json.loads(article['category'])
                        except:
                            article['category'] = []
                    return article
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting article by ID: {e}")
            return None
    
    def update_article_status(self, article_id: str, status: str) -> bool:
        """Update the status of an article."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    UPDATE articles
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status, datetime.now().isoformat(), article_id),
                )
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating article status: {e}")
            return False
    
    def update_article(self, article_id: str, updates: Dict[str, Any]) -> bool:
        """Update an article with new data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                params = []
                
                for key, value in updates.items():
                    if key in ['title', 'body', 'link', 'source', 'author', 'status']:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)
                    elif key == 'category':
                        set_clauses.append("category = ?")
                        params.append(json.dumps(value))
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(article_id)
                
                query = f"UPDATE articles SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, params)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating article: {e}")
            return False
    
    def delete_article(self, article_id: str) -> bool:
        """Delete an article from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting article: {e}")
            return False
    
    def get_article_stats(self) -> Dict[str, Any]:
        """Get statistics about articles in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total articles
                cursor.execute("SELECT COUNT(*) FROM articles")
                total = cursor.fetchone()[0]
                
                # Articles by status
                cursor.execute("SELECT status, COUNT(*) FROM articles GROUP BY status")
                status_counts = dict(cursor.fetchall())
                
                # Articles by source
                cursor.execute("SELECT source, COUNT(*) FROM articles GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10")
                source_counts = dict(cursor.fetchall())
                
                return {
                    "total_articles": total,
                    "status_counts": status_counts,
                    "source_counts": source_counts
                }
                
        except Exception as e:
            logger.error(f"Error getting article stats: {e}")
            return {}
    
    def save_setting(self, key: str, value: str) -> bool:
        """Save a setting to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, value, datetime.now().isoformat()))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving setting: {e}")
            return False
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                
                return row[0] if row else None
                
        except Exception as e:
            logger.error(f"Error getting setting: {e}")
            return None
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT key, value FROM settings")
                rows = cursor.fetchall()
                
                return dict(rows)
                
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return {}
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent application logs."""
        try:
            # For now, return empty list since we don't have a logs table
            # This can be implemented later if needed
            return []
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
    
    def migrate_from_json(self, json_file_path: str = "news.json") -> bool:
        """Migrate data from the old JSON file to SQLite."""
        try:
            json_path = Path(json_file_path)
            if not json_path.exists():
                logger.info("No JSON file to migrate from")
                return True
            
            with open(json_path, 'r') as f:
                articles = json.load(f)
            
            if not articles:
                logger.info("No articles to migrate")
                return True
            
            success = self.save_all_articles(articles)
            if success:
                # Backup the old file
                backup_path = json_path.with_suffix('.json.backup')
                json_path.rename(backup_path)
                logger.info(f"Migration completed. Old file backed up to {backup_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error migrating from JSON: {e}")
            return False

    def create_user(self, username: str, password: str, email: str = None) -> bool:
        """Create a new user with hashed password."""
        try:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email)
                    VALUES (?, ?, ?)
                ''', (username, password_hash, email or ""))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by username."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def verify_user(self, username: str, password: str) -> bool:
        """Verify a user's password."""
        user = self.get_user_by_username(username)
        if not user:
            return False
        try:
            return bcrypt.checkpw(password.encode(), user['password_hash'].encode())
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False


# Global database instance
_db_instance = None

def get_database() -> SQLiteDatabase:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = SQLiteDatabase()
    return _db_instance

def init_database():
    """Initialize the database and migrate from JSON if needed."""
    db = get_database()
    db.migrate_from_json()
    return db 
