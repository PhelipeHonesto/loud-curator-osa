import React, { useState, useEffect } from 'react';
import type { Article } from '../types';
import { getNews } from '../services/api';
import ArticleCard from '../components/ArticleCard';
import './Feed.css';

const Saved: React.FC = () => {
  const [savedArticles, setSavedArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');

  useEffect(() => {
    fetchSavedArticles();
  }, []);

  const fetchSavedArticles = async () => {
    try {
      setLoading(true);
      const articles = await getNews();
      // Filter for published/saved articles
      const savedArticles = articles.filter(article => 
        article.status === 'posted' || article.status === 'published'
      );
      setSavedArticles(savedArticles);
      setError(null);
    } catch (err) {
      setError('Failed to fetch saved articles');
      console.error('Error fetching saved articles:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: string, storyId: string) => {
    switch (action) {
      case 'select':
        // Handle select action for reposting
        console.log('Reposting article:', storyId);
        break;
      case 'edit':
        // Handle edit action
        console.log('Editing article:', storyId);
        break;
      case 'post':
        // Handle post action
        console.log('Posting article:', storyId);
        break;
      case 'post-figma':
        // Handle post-figma action
        console.log('Posting to Figma:', storyId);
        break;
    }
  };

  const getUniqueSources = () => {
    const sources = savedArticles.map(article => article.source);
    return ['all', ...Array.from(new Set(sources))];
  };

  const filteredArticles = savedArticles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         article.body?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || article.status === statusFilter;
    const matchesSource = sourceFilter === 'all' || article.source === sourceFilter;
    
    return matchesSearch && matchesStatus && matchesSource;
  });

  const getStatusCounts = () => {
    const counts = savedArticles.reduce((acc, article) => {
      acc[article.status] = (acc[article.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading) {
    return (
      <div className="feed-container">
        <div className="loading">Loading saved articles...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="feed-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="feed-container">
      <div className="feed-header">
        <h1>Saved Articles</h1>
        <div className="feed-controls">
          <input
            type="text"
            placeholder="Search saved articles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="all">All Status</option>
            <option value="posted">Posted</option>
            <option value="published">Published</option>
            <option value="edited">Edited</option>
          </select>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="source-filter"
          >
            {getUniqueSources().map(source => (
              <option key={source} value={source}>
                {source === 'all' ? 'All Sources' : source}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="saved-stats">
        <div className="stat-card">
          <h3>Total Saved</h3>
          <p>{savedArticles.length}</p>
        </div>
        <div className="stat-card">
          <h3>Posted</h3>
          <p>{statusCounts.posted || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Published</h3>
          <p>{statusCounts.published || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Showing</h3>
          <p>{filteredArticles.length}</p>
        </div>
      </div>

      <div className="articles-grid">
        {filteredArticles.length === 0 ? (
          <div className="no-articles">
            <h3>No saved articles found</h3>
            <p>
              {searchTerm || statusFilter !== 'all' || sourceFilter !== 'all' 
                ? 'Try adjusting your filters to see more articles.'
                : 'Published and posted articles will appear here.'
              }
            </p>
          </div>
        ) : (
          filteredArticles.map((article) => (
            <div key={article.id} className="article-card-container">
              <ArticleCard
                article={article}
                onAction={handleAction}
                isLoading={false}
              />
            </div>
          ))
        )}
      </div>

      <div className="saved-summary">
        <p>Total saved articles: {savedArticles.length}</p>
        <p>Showing: {filteredArticles.length}</p>
        {searchTerm && <p>Search term: "{searchTerm}"</p>}
      </div>
    </div>
  );
};

export default Saved;
