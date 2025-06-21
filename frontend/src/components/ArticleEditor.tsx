import { useState, useEffect } from 'react';
import type { Article } from '../types';
import './ArticleEditor.css';

interface ArticleEditorProps {
  article: Article;
  onSave: (article: Article) => void;
  onCancel: () => void;
  onPreview: (content: string) => void;
}

const ArticleEditor = ({ article, onSave, onCancel, onPreview }: ArticleEditorProps) => {
  const [editedArticle, setEditedArticle] = useState<Article>(article);
  const [isLoading, setIsLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState<'slack' | 'figma' | null>(null);
  const [slackPreview, setSlackPreview] = useState<string>('');

  useEffect(() => {
    generateSlackPreview();
  }, [editedArticle]);

  const handleInputChange = (field: keyof Article, value: string) => {
    setEditedArticle(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const generateSlackPreview = () => {
    const preview = `:newspaper: ${editedArticle.title}

${editedArticle.body}

Source: *${editedArticle.source}* | <${editedArticle.link}|Read Original>`;
    
    setSlackPreview(preview);
  };

  const generateFigmaPreview = () => {
    return `#title
${editedArticle.title}

#date
${editedArticle.date}

#body
${editedArticle.body}

#link
${editedArticle.link}`;
  };

  const handlePreview = (mode: 'slack' | 'figma') => {
    setPreviewMode(mode);
    if (mode === 'slack') {
      onPreview(slackPreview);
    } else {
      onPreview(generateFigmaPreview());
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await onSave(editedArticle);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAIGenerate = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/edit/${article.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const result = await response.json();
        if (result.body) {
          setEditedArticle(prev => ({
            ...prev,
            body: result.body
          }));
        }
      }
    } catch (error) {
      console.error('Error generating AI content:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="article-editor">
      <div className="editor-header">
        <h2>Edit Article</h2>
        <div className="editor-actions">
          <button 
            onClick={() => handlePreview('slack')}
            className="preview-btn slack"
            disabled={isLoading}
          >
            Preview Slack
          </button>
          <button 
            onClick={() => handlePreview('figma')}
            className="preview-btn figma"
            disabled={isLoading}
          >
            Preview Figma
          </button>
          <button 
            onClick={handleAIGenerate}
            className="ai-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'AI Rewrite'}
          </button>
          <button 
            onClick={handleSave}
            className="save-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
          <button 
            onClick={onCancel}
            className="cancel-btn"
            disabled={isLoading}
          >
            Cancel
          </button>
        </div>
      </div>

      <div className="editor-content">
        <div className="editor-section">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            type="text"
            value={editedArticle.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            className="title-input"
          />
        </div>

        <div className="editor-section">
          <label htmlFor="body">Content</label>
          <textarea
            id="body"
            value={editedArticle.body}
            onChange={(e) => handleInputChange('body', e.target.value)}
            className="content-textarea"
            rows={15}
            placeholder="Enter article content..."
          />
        </div>

        <div className="editor-section">
          <label>Source</label>
          <input
            type="text"
            value={editedArticle.source}
            onChange={(e) => handleInputChange('source', e.target.value)}
            className="source-input"
            readOnly
          />
        </div>

        <div className="editor-section">
          <label>Original Link</label>
          <input
            type="url"
            value={editedArticle.link}
            onChange={(e) => handleInputChange('link', e.target.value)}
            className="link-input"
          />
        </div>
      </div>

      {previewMode && (
        <div className="preview-panel">
          <div className="preview-header">
            <h3>{previewMode === 'slack' ? 'Slack Preview' : 'Figma Preview'}</h3>
            <button 
              onClick={() => setPreviewMode(null)}
              className="close-preview-btn"
            >
              ×
            </button>
          </div>
          <div className="preview-content">
            {previewMode === 'slack' ? (
              <div className="slack-preview">
                <div className="slack-message">
                  <div className="slack-header">
                    <span className="slack-icon">📰</span>
                    <span className="slack-title">{editedArticle.title}</span>
                  </div>
                  <div className="slack-body">{editedArticle.body}</div>
                  <div className="slack-footer">
                    Source: <strong>{editedArticle.source}</strong> | 
                    <a href={editedArticle.link} target="_blank" rel="noopener noreferrer">
                      Read Original
                    </a>
                  </div>
                </div>
              </div>
            ) : (
              <div className="figma-preview">
                <pre>{generateFigmaPreview()}</pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticleEditor; 