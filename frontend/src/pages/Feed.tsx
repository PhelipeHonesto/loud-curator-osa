import { useEffect, useState, useCallback } from 'react';
import ArticleCard from '../components/ArticleCard';
import * as api from '../services/api';
import type { Article } from '../types';
import './Feed.css';

const Feed = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [actingArticleId, setActingArticleId] = useState<string | null>(null);

  const loadNews = useCallback(() => {
    setActingArticleId('loading_feed');
    setError(null);
    api.getNews()
      .then(setArticles)
      .catch(() => setError('Could not load news. Please try again later.'))
      .finally(() => setActingArticleId(null));
  }, []);

  useEffect(() => {
    loadNews();
  }, [loadNews]);

  const handleIngestNews = async () => {
    setActingArticleId('ingesting');
    setMessage('Ingesting new articles...');
    setError(null);
    try {
      const response = await api.ingestNews();
      setMessage(response.message);
      loadNews(); // Refresh the feed
    } catch (err: any) {
      setError(err.message || 'Ingestion failed.');
    } finally {
      setActingArticleId(null);
    }
  };

  const handleAction = async (action: 'select' | 'edit' | 'post', storyId: string) => {
    setActingArticleId(storyId);
    setMessage(null);
    setError(null);

    const actionMap = {
      select: {
        apiCall: api.selectStory,
        loadingMessage: 'Selecting story...',
        successMessage: 'Story selected.',
      },
      edit: {
        apiCall: api.editStory,
        loadingMessage: 'Editing with AI...',
        successMessage: 'Story edited.',
      },
      post: {
        apiCall: api.postToSlack,
        loadingMessage: 'Posting to Slack...',
        successMessage: 'Story posted to Slack.',
      },
    };

    try {
      setMessage(actionMap[action].loadingMessage);
      await actionMap[action].apiCall(storyId);
      setMessage(actionMap[action].successMessage);
      // Refresh the specific article without reloading the whole feed for a smoother experience
      const updatedNews = await api.getNews();
      setArticles(updatedNews);
    } catch (err: any) {
      setError(err.message || `Action '${action}' failed.`);
    } finally {
      setActingArticleId(null);
      // Clear the message after a few seconds
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const isLoading = (id?: string) => {
    if (!actingArticleId) return false;
    if (actingArticleId === 'loading_feed' || actingArticleId === 'ingesting') return true;
    if (id) return actingArticleId === id;
    return false;
  };

  return (
    <div>
      <div className="feed-header">
        <h1>News Feed</h1>
        <button onClick={handleIngestNews} disabled={isLoading()}>
          {isLoading() ? 'Loading...' : 'Update News'}
        </button>
      </div>

      {error && <p className="message error">{error}</p>}
      {message && <p className="message success">{message}</p>}
      
      {isLoading() && articles.length === 0 ? (
        <p>Loading news feed...</p>
      ) : (
        <div className="articles-container">
          {articles.map(article => (
            <ArticleCard 
              key={article.id} 
              article={article} 
              onAction={handleAction}
              isLoading={isLoading(article.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Feed;
