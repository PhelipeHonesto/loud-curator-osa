import { useEffect, useState, useCallback } from 'react';
import ArticleCard from '../components/ArticleCard';
import * as api from '../services/api';
import type { Article } from '../types';
import './Feed.css';

const Feed = () => {
  // Component State
  const [articles, setArticles] = useState<Article[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  
  // Tracks the ID of the article currently being processed by an action,
  // or a general status like 'loading_feed' or 'ingesting'.
  const [actingArticleId, setActingArticleId] = useState<string | null>(null);

  /**
   * Fetches all news from the API and updates the component's state.
   * This function is memoized with useCallback to prevent re-creation on every render.
   */
  const loadNews = useCallback(() => {
    setActingArticleId('loading_feed');
    setError(null);
    api.getNews()
      .then(setArticles)
      .catch(() => setError('Could not load news. Please try again later.'))
      .finally(() => setActingArticleId(null));
  }, []);

  // Load news once when the component mounts.
  useEffect(() => {
    loadNews();
  }, [loadNews]);

  /**
   * Triggers the backend to ingest new articles from all sources,
   * then reloads the news feed to display them.
   */
  const handleIngestNews = async () => {
    setActingArticleId('ingesting');
    setMessage('Ingesting new articles...');
    setError(null);
    try {
      const response = await api.ingestNews();
      setMessage(response.message);
      loadNews(); // Refresh the feed
    } catch (err: any) {
      const errorMessage = err.message || 'An unknown error occurred during ingestion.';
      setError(errorMessage);
    } finally {
      setActingArticleId(null);
      setTimeout(() => setMessage(null), 5000);
    }
  };

  /**
   * Handles user actions on an article card (e.g., select, edit, post).
   * @param action The type of action to perform.
   * @param storyId The ID of the target article.
   */
  const handleAction = async (action: 'select' | 'edit' | 'post', storyId: string) => {
    setActingArticleId(storyId);
    setMessage(null);
    setError(null);

    // Maps action types to their respective API calls and UI messages.
    const actionMap = {
      select: { apiCall: api.selectStory, loadingMessage: 'Selecting story...' },
      edit: { apiCall: api.editStory, loadingMessage: 'Editing with AI...' },
      post: { apiCall: api.postToSlack, loadingMessage: 'Posting to Slack...' },
    };

    try {
      const currentAction = actionMap[action];
      setMessage(currentAction.loadingMessage);
      
      const response = await currentAction.apiCall(storyId);
      setMessage(response.message);

      // After a successful action, reload all news to reflect the change.
      // This is a simple but less efficient approach. A future optimization
      // would be to have the API return the updated article and update it in the local state.
      loadNews();
    } catch (err: any) {
      const errorMessage = err.message || `An unknown error occurred while performing action: ${action}.`;
      setError(errorMessage);
    } finally {
      setActingArticleId(null);
      // Clear the message after a few seconds
      setTimeout(() => setMessage(null), 5000);
    }
  };

  /**
   * A helper function to determine if an action is currently in progress.
   * Used to disable buttons and show loading indicators.
   * @param id The optional ID of a specific article to check.
   * @returns boolean indicating if the UI should be in a loading state.
   */
  const isLoading = (id?: string) => {
    if (!actingArticleId) return false;
    // General loading states
    if (actingArticleId === 'loading_feed' || actingArticleId === 'ingesting') return true;
    // Specific article loading state
    if (id) return actingArticleId === id;
    return false;
  };

  return (
    <div>
      <div className="feed-header">
        <h1>News Feed</h1>
        <button onClick={handleIngestNews} disabled={isLoading()}>
          {isLoading('ingesting') ? 'Ingesting...' : (isLoading('loading_feed') ? 'Loading...' : 'Update News')}
        </button>
      </div>

      {/* Display error or success messages */}
      {error && <p className="message error">{error}</p>}
      {message && <p className="message success">{message}</p>}
      
      {/* Display a loading message or the list of articles */}
      {isLoading('loading_feed') && articles.length === 0 ? (
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
