import React, { useState, useEffect } from 'react';
import type { Article } from '../types';
import { getNews } from '../services/api';
import ArticleCard from '../components/ArticleCard';
import ArticleEditor from '../components/ArticleEditor';
import './Feed.css';

const Drafts: React.FC = () => {
  const [drafts, setDrafts] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('draft');

  useEffect(() => {
    fetchDrafts();
  }, []);

  const fetchDrafts = async () => {
    try {
      setLoading(true);
      const articles = await getNews();
      // Filter for draft status articles
      const draftArticles = articles.filter(article => article.status === 'draft');
      setDrafts(draftArticles);
      setError(null);
    } catch (err) {
      setError('Failed to fetch drafts');
      console.error('Error fetching drafts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (article: Article) => {
    setEditingArticle(article);
  };

  const handleSave = async (updatedArticle: Article) => {
    try {
      // Update the article in the local state
      setDrafts(drafts.map(draft => 
        draft.id === updatedArticle.id ? updatedArticle : draft
      ));
      setEditingArticle(null);
    } catch (err) {
      console.error('Error saving article:', err);
    }
  };

  const handlePreview = (content: string) => {
    // Handle preview functionality
    console.log('Preview content:', content);
  };

  const handleAction = async (action: string, storyId: string) => {
    switch (action) {
      case 'edit':
        const articleToEdit = drafts.find(draft => draft.id === storyId);
        if (articleToEdit) {
          handleEdit(articleToEdit);
        }
        break;
      case 'select':
        // Handle select action
        break;
      case 'post':
        // Handle post action
        break;
      case 'post-figma':
        // Handle post-figma action
        break;
    }
  };

  const filteredDrafts = drafts.filter(draft =>
    draft.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    draft.body?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="feed-container">
        <div className="loading">Loading drafts...</div>
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
        <h1>Drafts</h1>
        <div className="feed-controls">
          <input
            type="text"
            placeholder="Search drafts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="draft">Draft</option>
            <option value="review">Review</option>
            <option value="pending">Pending</option>
          </select>
        </div>
      </div>

      {editingArticle && (
        <div className="editor-overlay">
          <div className="editor-container">
            <ArticleEditor
              article={editingArticle}
              onSave={handleSave}
              onCancel={() => setEditingArticle(null)}
              onPreview={handlePreview}
            />
          </div>
        </div>
      )}

      <div className="articles-grid">
        {filteredDrafts.length === 0 ? (
          <div className="no-articles">
            <h3>No drafts found</h3>
            <p>Start creating content to see your drafts here.</p>
          </div>
        ) : (
          filteredDrafts.map((draft) => (
            <div key={draft.id} className="article-card-container">
              <ArticleCard
                article={draft}
                onAction={handleAction}
                isLoading={false}
              />
            </div>
          ))
        )}
      </div>

      <div className="drafts-summary">
        <p>Total drafts: {drafts.length}</p>
        <p>Showing: {filteredDrafts.length}</p>
      </div>
    </div>
  );
};

export default Drafts;
