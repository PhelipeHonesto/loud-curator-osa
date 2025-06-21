import pytest
import json
import tempfile
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Import the modules to test
from agents.rss_agent import (
    fetch_rss_feed, fetch_multiple_rss_feeds, fetch_custom_rss_feeds,
    extract_content, parse_date, clean_text, extract_categories,
    validate_rss_feed, get_feed_info, fetch_aviation_rss_feeds
)
from scheduler import NewsScheduler, init_scheduler, get_scheduler
from logging_config import (
    setup_logging, get_logger, log_request, log_api_call,
    log_article_processing, log_scheduler_event, get_log_files,
    get_log_stats, clear_logs
)


class TestRSSAgent:
    """Test cases for RSS agent functionality."""
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test HTML entity removal
        assert clean_text("&amp; &lt; &gt;") == "  "
        
        # Test whitespace normalization
        assert clean_text("  multiple    spaces  ") == "multiple spaces"
        
        # Test empty input
        assert clean_text("") == ""
        assert clean_text(None) == ""  # type: ignore
    
    def test_extract_categories(self):
        """Test category extraction from RSS entries."""
        # Mock RSS entry with tags
        mock_entry = Mock()
        mock_entry.tags = [Mock(term="aviation"), Mock(term="news")]
        mock_entry.category = "business"
        
        categories = extract_categories(mock_entry)
        assert "aviation" in categories
        assert "news" in categories
        assert "business" in categories
    
    def test_parse_date(self):
        """Test date parsing from RSS entries."""
        # Mock RSS entry with published_parsed
        mock_entry = Mock()
        mock_entry.published_parsed = (2023, 1, 15, 10, 30, 0, 0, 0, 0)
        
        date = parse_date(mock_entry)
        assert isinstance(date, datetime)
        assert date.year == 2023
        assert date.month == 1
        assert date.day == 15
    
    def test_parse_date_fallback(self):
        """Test date parsing fallback to current time."""
        # Mock RSS entry without date fields
        mock_entry = Mock()
        mock_entry.published_parsed = None
        mock_entry.updated_parsed = None
        mock_entry.created_parsed = None
        
        date = parse_date(mock_entry)
        assert isinstance(date, datetime)
        # Should be close to current time
        assert abs((datetime.now() - date).total_seconds()) < 10
    
    @patch('agents.rss_agent.feedparser')
    def test_validate_rss_feed_valid(self, mock_feedparser):
        """Test RSS feed validation with valid feed."""
        mock_feed = Mock()
        mock_feed.entries = [Mock(), Mock(), Mock()]
        mock_feedparser.parse.return_value = mock_feed
        
        assert validate_rss_feed("https://example.com/feed.xml") is True
    
    @patch('agents.rss_agent.feedparser')
    def test_validate_rss_feed_invalid(self, mock_feedparser):
        """Test RSS feed validation with invalid feed."""
        mock_feed = Mock()
        mock_feed.entries = []
        mock_feedparser.parse.return_value = mock_feed
        
        assert validate_rss_feed("https://example.com/feed.xml") is False
    
    @patch('agents.rss_agent.feedparser')
    def test_get_feed_info(self, mock_feedparser):
        """Test getting feed information."""
        mock_feed = Mock()
        mock_feed.feed.get.side_effect = lambda key, default="": {
            "title": "Test Feed",
            "description": "Test Description", 
            "link": "https://example.com",
            "language": "en",
            "updated": "2023-01-15"
        }.get(key, default)
        mock_feed.entries = [Mock(), Mock()]
        mock_feedparser.parse.return_value = mock_feed
        
        info = get_feed_info("https://example.com/feed.xml")
        
        assert info["title"] == "Test Feed"
        assert info["description"] == "Test Description"
        assert info["entry_count"] == 2
        assert info["is_valid"] is True
    
    @patch('agents.rss_agent.feedparser')
    def test_fetch_rss_feed(self, mock_feedparser):
        """Test fetching articles from RSS feed."""
        # Mock feedparser response
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.feed.get.side_effect = lambda key, default="": {
            "title": "Test Feed"
        }.get(key, default)
        
        mock_entry = Mock()
        mock_entry.get.return_value = "Test Article"
        mock_entry.link = "https://example.com/article"
        mock_entry.author = "Test Author"
        
        # Mock content extraction
        with patch('agents.rss_agent.extract_content', return_value="Test content"):
            with patch('agents.rss_agent.parse_date', return_value=datetime.now()):
                mock_feed.entries = [mock_entry]
                mock_feedparser.parse.return_value = mock_feed
                
                articles = fetch_rss_feed("https://example.com/feed.xml", "Test Source")
                
                assert len(articles) == 1
                assert articles[0]["title"] == "Test Article"
                assert articles[0]["source"] == "Test Source"
                assert articles[0]["status"] == "new"


class TestScheduler:
    """Test cases for scheduler functionality."""
    
    def setup_method(self):
        """Setup method for each test."""
        self.mock_ingest_callback = Mock(return_value={"message": "Ingestion completed"})
        self.mock_post_callback = Mock(return_value={"message": "Posting completed"})
        
        # Create temporary file for schedules
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.write('{"ingestion": {"enabled": false}, "posting": {"enabled": false}}')
        self.temp_file.close()
    
    def teardown_method(self):
        """Teardown method for each test."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback, self.mock_post_callback)
            
            assert scheduler.ingest_callback == self.mock_ingest_callback
            assert scheduler.post_callback == self.mock_post_callback
            assert scheduler.is_running is False
    
    def test_set_ingestion_schedule(self):
        """Test setting ingestion schedule."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback)
            scheduler.set_ingestion_schedule(True, "daily", "09:00")
            
            assert scheduler.schedules["ingestion"]["enabled"] is True
            assert scheduler.schedules["ingestion"]["frequency"] == "daily"
            assert scheduler.schedules["ingestion"]["time"] == "09:00"
    
    def test_set_posting_schedule(self):
        """Test setting posting schedule."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback, self.mock_post_callback)
            scheduler.set_posting_schedule(True, "weekly", "10:00", ["monday", "tuesday"])
            
            assert scheduler.schedules["posting"]["enabled"] is True
            assert scheduler.schedules["posting"]["frequency"] == "weekly"
            assert scheduler.schedules["posting"]["time"] == "10:00"
            assert scheduler.schedules["posting"]["days"] == ["monday", "tuesday"]
    
    def test_run_now_ingestion(self):
        """Test running ingestion job immediately."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback)
            scheduler.run_now("ingestion")
            
            self.mock_ingest_callback.assert_called_once()
    
    def test_run_now_posting(self):
        """Test running posting job immediately."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback, self.mock_post_callback)
            scheduler.run_now("posting")
            
            self.mock_post_callback.assert_called_once()
    
    def test_get_status(self):
        """Test getting scheduler status."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback)
            status = scheduler.get_status()
            
            assert "is_running" in status
            assert "schedules" in status
            assert "next_run" in status
    
    def test_start_stop_scheduler(self):
        """Test starting and stopping scheduler."""
        with patch('scheduler.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            scheduler = NewsScheduler(self.mock_ingest_callback)
            
            # Test start
            scheduler.start()
            assert scheduler.is_running is True
            
            # Test stop
            scheduler.stop()
            assert scheduler.is_running is False


class TestLogging:
    """Test cases for logging functionality."""
    
    def setup_method(self):
        """Setup method for each test."""
        # Create temporary logs directory
        self.temp_logs_dir = tempfile.mkdtemp()
        self.original_logs_dir = Path("logs")
        
        # Patch the logs directory
        with patch('logging_config.logs_dir', Path(self.temp_logs_dir)):
            setup_logging(enable_file=False)  # Disable file logging for tests
    
    def teardown_method(self):
        """Teardown method for each test."""
        import shutil
        shutil.rmtree(self.temp_logs_dir, ignore_errors=True)
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_log_request(self):
        """Test request logging."""
        logger = get_logger("test_request")
        
        # This should not raise an exception
        log_request(logger, "GET", "/api/test", 200, 0.5, "test-agent", "127.0.0.1")
    
    def test_log_api_call(self):
        """Test API call logging."""
        logger = get_logger("test_api")
        
        # Test successful API call
        log_api_call(logger, "TestAPI", "/test", True, 0.3)
        
        # Test failed API call
        log_api_call(logger, "TestAPI", "/test", False, 0.3, "Connection error")
    
    def test_log_article_processing(self):
        """Test article processing logging."""
        logger = get_logger("test_article")
        
        # Test successful processing
        log_article_processing(logger, "select", "test-id", "test-source", True)
        
        # Test failed processing
        log_article_processing(logger, "select", "test-id", "test-source", False, "Database error")
    
    def test_log_scheduler_event(self):
        """Test scheduler event logging."""
        logger = get_logger("test_scheduler")
        
        # Test successful event
        log_scheduler_event(logger, "start", "ingestion", True, {"articles": 5})
        
        # Test failed event
        log_scheduler_event(logger, "run", "posting", False, error_message="Network error")
    
    def test_get_log_files(self):
        """Test getting log files list."""
        # Create a test log file
        test_log_file = Path(self.temp_logs_dir) / "test.log"
        test_log_file.write_text("test content")
        
        with patch('logging_config.logs_dir', Path(self.temp_logs_dir)):
            log_files = get_log_files()
            assert "test.log" in log_files
    
    def test_get_log_stats(self):
        """Test getting log statistics."""
        # Create a test log file
        test_log_file = Path(self.temp_logs_dir) / "test.log"
        test_log_file.write_text("test content")
        
        with patch('logging_config.logs_dir', Path(self.temp_logs_dir)):
            stats = get_log_stats()
            assert stats["total_files"] == 1
            assert "test.log" in stats["files"]
            assert stats["files"]["test.log"]["size"] > 0


class TestDeduplication:
    """Test cases for article deduplication functionality."""
    
    def test_deduplicate_articles_exact_link_match(self):
        """Test deduplication with exact link matches."""
        from main import deduplicate_articles
        
        new_articles = [
            {"id": "1", "title": "Test Article 1", "link": "https://example.com/1", "source": "Test"},
            {"id": "2", "title": "Test Article 2", "link": "https://example.com/2", "source": "Test"}
        ]
        
        existing_articles = [
            {"id": "3", "title": "Existing Article", "link": "https://example.com/1", "source": "Test"}
        ]
        
        unique_articles = deduplicate_articles(new_articles, existing_articles)
        
        assert len(unique_articles) == 1
        assert unique_articles[0]["id"] == "2"
    
    def test_deduplicate_articles_exact_title_match(self):
        """Test deduplication with exact title matches."""
        from main import deduplicate_articles
        
        new_articles = [
            {"id": "1", "title": "Test Article", "link": "https://example.com/1", "source": "Test"},
            {"id": "2", "title": "Another Article", "link": "https://example.com/2", "source": "Test"}
        ]
        
        existing_articles = [
            {"id": "3", "title": "Test Article", "link": "https://example.com/3", "source": "Test"}
        ]
        
        unique_articles = deduplicate_articles(new_articles, existing_articles)
        
        assert len(unique_articles) == 1
        assert unique_articles[0]["id"] == "2"
    
    def test_deduplicate_articles_similar_title(self):
        """Test deduplication with similar titles."""
        from main import deduplicate_articles
        
        new_articles = [
            {"id": "1", "title": "Test Article About Aviation", "link": "https://example.com/1", "source": "Test"},
            {"id": "2", "title": "Another Article", "link": "https://example.com/2", "source": "Test"}
        ]
        
        existing_articles = [
            {"id": "3", "title": "Test Article About Aviation News", "link": "https://example.com/3", "source": "Test"}
        ]
        
        unique_articles = deduplicate_articles(new_articles, existing_articles)
        
        assert len(unique_articles) == 1
        assert unique_articles[0]["id"] == "2"
    
    def test_deduplicate_articles_no_duplicates(self):
        """Test deduplication with no duplicates."""
        from main import deduplicate_articles
        
        new_articles = [
            {"id": "1", "title": "Test Article 1", "link": "https://example.com/1", "source": "Test"},
            {"id": "2", "title": "Test Article 2", "link": "https://example.com/2", "source": "Test"}
        ]
        
        existing_articles = [
            {"id": "3", "title": "Existing Article", "link": "https://example.com/3", "source": "Test"}
        ]
        
        unique_articles = deduplicate_articles(new_articles, existing_articles)
        
        # Both articles should be unique since they have different titles and links
        assert len(unique_articles) == 2
        assert unique_articles[0]["id"] == "1"
        assert unique_articles[1]["id"] == "2"


class TestIntegration:
    """Integration tests for the enhanced features."""
    
    @patch('agents.rss_agent.feedparser')
    def test_rss_integration_with_main(self, mock_feedparser):
        """Test RSS integration with main ingestion process."""
        from main import ingest_news
        
        # Mock RSS feed response
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.feed.title = "Test Feed"
        
        mock_entry = Mock()
        mock_entry.get.return_value = "Test Article"
        mock_entry.link = "https://example.com/article"
        mock_entry.author = "Test Author"
        
        with patch('agents.rss_agent.extract_content', return_value="Test content"):
            with patch('agents.rss_agent.parse_date', return_value=datetime.now()):
                mock_feed.entries = [mock_entry]
                mock_feedparser.parse.return_value = mock_feed
                
                # Mock other agents to return empty lists
                with patch('agents.aviation_pages_reader.fetch_skywest_news', return_value=[]):
                    with patch('agents.newsdata_agent.fetch_newsdata_news', return_value=[]):
                        with patch('agents.institutional_reader.fetch_institutional_news', return_value=[]):
                            with patch('agents.groundnews_agent.fetch_groundnews_articles', return_value=[]):
                                with patch('database.get_all_news', return_value=[]):
                                    with patch('database.save_all_news'):
                                        result = ingest_news()
                                        
                                        assert "Successfully ingested" in result["message"]
    
    def test_scheduler_integration(self):
        """Test scheduler integration with main application."""
        mock_ingest_callback = Mock(return_value={"message": "Ingestion completed"})
        
        # Test scheduler initialization
        scheduler = init_scheduler(mock_ingest_callback)
        assert scheduler is not None
        
        # Test getting scheduler instance
        scheduler_instance = get_scheduler()
        assert scheduler_instance == scheduler
        
        # Test running job
        scheduler.run_now("ingestion")
        mock_ingest_callback.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 
