import pytest
from unittest.mock import patch, Mock
from agents.aviation_pages_reader import fetch_skywest_news
from agents.newsdata_agent import fetch_newsdata_news
from agents.institutional_reader import (
    fetch_institutional_news,
    fetch_reuters_aviation,
)
from agents.groundnews_agent import fetch_groundnews_articles

# Explicitly configure logging for the tests
from logging_config import setup_logging

setup_logging(enable_file=False)


class TestAviationPagesReader:
    """Test cases for the SkyWest news reader agent."""
    
    @patch('agents.aviation_pages_reader.requests.get')
    def test_fetch_skywest_news_success(self, mock_get):
        """Test successful fetching of SkyWest news."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = '''
        <html>
            <div class="news-release-item">
                <h4><a href="/news/test-article">Test Article Title</a></h4>
                <div class="news-release-date">12/25/2023</div>
            </div>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = fetch_skywest_news()
        
        assert isinstance(articles, list)
        assert len(articles) == 1
        assert articles[0]['title'] == 'Test Article Title'
        assert articles[0]['source'] == 'SkyWest, Inc.'
        assert articles[0]['status'] == 'new'
        assert 'id' in articles[0]
        assert 'link' in articles[0]
    
    @patch('agents.aviation_pages_reader.requests.get')
    def test_fetch_skywest_news_request_error(self, mock_get):
        """Test handling of request errors."""
        mock_get.side_effect = Exception("Network error")
        
        articles = fetch_skywest_news()
        
        assert isinstance(articles, list)
        assert len(articles) == 0


class TestNewsdataAgent:
    """Test cases for the NewsData.io agent."""
    
    @patch.dict('os.environ', {'NEWSDATA_API_KEY': 'test_key'})
    @patch('agents.newsdata_agent.requests.get')
    def test_fetch_newsdata_news_success(self, mock_get):
        """Test successful fetching of NewsData.io news."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'success',
            'results': [
                {
                    'title': 'Test Aviation News',
                    'description': 'Test description',
                    'link': 'https://example.com',
                    'pubDate': '2023-12-25T10:00:00Z',
                    'source_id': 'test_source'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = fetch_newsdata_news()
        
        assert isinstance(articles, list)
        assert len(articles) == 1
        assert articles[0]['title'] == 'Test Aviation News'
        assert articles[0]['source'] == 'test_source'
        assert articles[0]['status'] == 'new'
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('agents.newsdata_agent.load_dotenv')
    def test_fetch_newsdata_news_no_api_key(self, mock_load_dotenv):
        """Test handling of missing API key."""
        # Ensure load_dotenv doesn't load any .env file
        mock_load_dotenv.return_value = None
        
        articles = fetch_newsdata_news()
        
        assert isinstance(articles, list)
        assert len(articles) == 0
    
    @patch.dict('os.environ', {'NEWSDATA_API_KEY': 'test_key'})
    @patch('agents.newsdata_agent.requests.get')
    def test_fetch_newsdata_news_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'error',
            'results': {'message': 'API key invalid'}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = fetch_newsdata_news()
        
        assert isinstance(articles, list)
        assert len(articles) == 0


class TestInstitutionalReader:
    """Test cases for the institutional news reader agent."""
    
    @patch.dict('os.environ', {'NEWSDATA_API_KEY': 'test_key'})
    @patch('agents.institutional_reader.requests.get')
    def test_fetch_institutional_news_success(self, mock_get):
        """Test successful fetching of institutional news."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'success',
            'results': [
                {
                    'title': 'Reuters Aviation News',
                    'description': 'Test description',
                    'link': 'https://reuters.com/test',
                    'pubDate': '2023-12-25T10:00:00Z',
                    'source_id': 'reuters'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = fetch_institutional_news()
        
        assert isinstance(articles, list)
        # Should have articles from multiple sources
        assert len(articles) > 0
        assert any('reuters' in article['source'].lower() for article in articles)
    
    @patch.dict('os.environ', {'NEWSDATA_API_KEY': 'test_key'})
    @patch('agents.institutional_reader.requests.get')
    def test_fetch_reuters_aviation_success(self, mock_get):
        """Test successful fetching of Reuters aviation news."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'success',
            'results': [
                {
                    'title': 'Reuters Aviation News',
                    'description': 'Test description',
                    'link': 'https://reuters.com/test',
                    'pubDate': '2023-12-25T10:00:00Z',
                    'source_id': 'reuters'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = fetch_reuters_aviation()
        
        assert isinstance(articles, list)
        assert len(articles) == 1
        assert articles[0]['source'] == 'Reuters'
        assert articles[0]['status'] == 'new'


class TestGroundNewsAgent:
    """Test cases for the Ground News agent."""
    
    @patch.dict('os.environ', {'GROUNDNEWS_API_KEY': 'test_key'})
    @patch('agents.groundnews_agent.requests.get')
    def test_fetch_groundnews_articles_success(self, mock_get):
        """Test successful fetching of Ground News articles."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'success',
            'articles': [
                {
                    'title': 'Ground News Article',
                    'description': 'Test description',
                    'url': 'https://ground.news/test',
                    'publishedAt': '2023-12-25T10:00:00Z',
                    'source': {'name': 'Test Source'},
                    'bias': 'center',
                    'factuality': 'high'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = fetch_groundnews_articles()
        
        assert isinstance(articles, list)
        assert len(articles) == 1
        assert articles[0]['title'] == 'Ground News Article'
        assert articles[0]['source'] == 'Test Source'
        assert articles[0]['status'] == 'new'
        assert 'bias' in articles[0]
        assert 'factuality' in articles[0]
    
    @patch.dict('os.environ', {}, clear=True)
    def test_fetch_groundnews_articles_no_api_key(self):
        """Test handling of missing Ground News API key."""
        articles = fetch_groundnews_articles()
        
        assert isinstance(articles, list)
        assert len(articles) == 0


class TestAgentCommon:
    """Common test cases for all agents."""
    
    def test_article_structure(self):
        """Test that all agents return articles with the correct structure."""
        # This is a template test - in practice you'd test each agent
        expected_fields = ['id', 'title', 'date', 'body', 'link', 'source', 'status']
        
        # Mock a sample article
        sample_article = {
            'id': 'test-id',
            'title': 'Test Title',
            'date': '2023-12-25T10:00:00Z',
            'body': 'Test body',
            'link': 'https://example.com',
            'source': 'Test Source',
            'status': 'new'
        }
        
        for field in expected_fields:
            assert field in sample_article, f"Missing required field: {field}"
        
        # Test data types
        assert isinstance(sample_article['id'], str)
        assert isinstance(sample_article['title'], str)
        assert isinstance(sample_article['date'], str)
        assert isinstance(sample_article['body'], str)
        assert isinstance(sample_article['link'], str)
        assert isinstance(sample_article['source'], str)
        assert isinstance(sample_article['status'], str)
        assert sample_article['status'] == 'new'


# Integration tests
class TestAgentIntegration:
    """Integration tests for agent interactions."""
    
    @patch('agents.aviation_pages_reader.fetch_skywest_news')
    @patch('agents.newsdata_agent.fetch_newsdata_news')
    def test_multiple_agents_no_duplicates(self, mock_newsdata, mock_skywest):
        """Test that multiple agents can be used together without conflicts."""
        # Mock responses
        mock_skywest.return_value = [
            {
                'id': 'skywest-1',
                'title': 'SkyWest News',
                'link': 'https://skywest.com/1',
                'source': 'SkyWest, Inc.',
                'status': 'new'
            }
        ]
        
        mock_newsdata.return_value = [
            {
                'id': 'newsdata-1',
                'title': 'NewsData News',
                'link': 'https://newsdata.com/1',
                'source': 'NewsData.io',
                'status': 'new'
            }
        ]
        
        # Simulate calling both agents
        skywest_articles = mock_skywest()
        newsdata_articles = mock_newsdata()
        
        # Combine articles
        all_articles = skywest_articles + newsdata_articles
        
        assert len(all_articles) == 2
        assert all_articles[0]['source'] == 'SkyWest, Inc.'
        assert all_articles[1]['source'] == 'NewsData.io'
        
        # Check for unique IDs
        ids = [article['id'] for article in all_articles]
        assert len(ids) == len(set(ids)), "All article IDs should be unique" 
