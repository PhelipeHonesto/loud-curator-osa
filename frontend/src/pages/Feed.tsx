import { useEffect, useState, useCallback } from 'react';
import ArticleCard from '../components/ArticleCard';
import HeadlineRemixModal from '../components/HeadlineRemixModal';
import ArticleScoring from '../components/ArticleScoring';
import * as api from '../services/api';
import type { Article } from '../types';
import './Feed.css';

interface FilterPreset {
  id: string;
  name: string;
  filters: {
    searchTerm: string;
    statusFilter: string;
    sourceFilter: string;
    dateFrom: string;
    dateTo: string;
    advancedSearch: {
      titleOnly: boolean;
      bodyOnly: boolean;
      sourceOnly: boolean;
    };
  };
}

const Feed = () => {
  // Component State
  const [articles, setArticles] = useState<Article[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState<boolean>(false);
  const [advancedSearch, setAdvancedSearch] = useState({
    titleOnly: false,
    bodyOnly: false,
    sourceOnly: false,
  });
  const [filterPresets, setFilterPresets] = useState<FilterPreset[]>([]);
  const [showPresets, setShowPresets] = useState<boolean>(false);
  
  // Tracks the ID of the article currently being processed by an action,
  // or a general status like 'loading_feed' or 'ingesting'.
  const [actingArticleId, setActingArticleId] = useState<string | null>(null);

  // Headline remix modal state
  const [remixModalOpen, setRemixModalOpen] = useState(false);
  const [remixArticleId, setRemixArticleId] = useState<string | null>(null);
  const [remixArticleTitle, setRemixArticleTitle] = useState<string>('');
  const [remixOptions, setRemixOptions] = useState<string[]>([]);
  const [isRemixing, setIsRemixing] = useState(false);

  // Article scoring modal state
  const [scoringModalOpen, setScoringModalOpen] = useState(false);
  const [scoringArticle, setScoringArticle] = useState<Article | null>(null);

  /**
   * Fetches all news from the API and updates the component's state.
   * This function is memoized with useCallback to prevent re-creation on every render.
   */
  const loadNews = useCallback(() => {
    setActingArticleId('loading_feed');
    setError(null);
    api.getNews()
      .then(setArticles)
      .catch((err) => {
        if (err instanceof Error && err.message.includes('Failed to fetch')) {
          setError('Could not connect to the backend. Please ensure the server is running and try again.');
        } else {
          setError('Could not load news. Please try again later.');
        }
      })
      .finally(() => setActingArticleId(null));
  }, []);

  // Load news once when the component mounts.
  useEffect(() => {
    loadNews();
    loadFilterPresets();
  }, [loadNews]);

  // Load filter presets from localStorage
  const loadFilterPresets = () => {
    try {
      const saved = localStorage.getItem('filterPresets');
      if (saved) {
        setFilterPresets(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading filter presets:', error);
    }
  };

  // Save filter presets to localStorage
  const saveFilterPresets = (presets: FilterPreset[]) => {
    try {
      localStorage.setItem('filterPresets', JSON.stringify(presets));
    } catch (error) {
      console.error('Error saving filter presets:', error);
    }
  };

  /**
   * Updates a specific article in the local state without reloading all news.
   * @param articleId The ID of the article to update
   * @param updates The updates to apply to the article
   */
  const updateArticleInState = useCallback((articleId: string, updates: Partial<Article>) => {
    setArticles(prevArticles => 
      prevArticles.map(article => 
        article.id === articleId ? { ...article, ...updates } : article
      )
    );
  }, []);

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
      loadNews(); // Refresh the feed to get new articles
    } catch (err: any) {
      const errorMessage = err.message || 'An unknown error occurred during ingestion.';
      if (errorMessage.includes('Failed to fetch')) {
        setError('Could not connect to the backend. Please ensure the server is running and try again.');
      } else {
        setError(errorMessage);
      }
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
  const handleAction = async (action: 'select' | 'edit' | 'post' | 'post-figma' | 'remix' | 'score', storyId: string) => {
    if (action === 'remix') {
      handleRemixAction(storyId);
      return;
    }

    if (action === 'score') {
      handleScoreAction(storyId);
      return;
    }

    setActingArticleId(storyId);
    setMessage(null);
    setError(null);

    // Maps action types to their respective API calls and UI messages.
    const actionMap = {
      select: { 
        apiCall: api.selectStory, 
        loadingMessage: 'Selecting story...',
        successStatus: 'selected'
      },
      edit: { 
        apiCall: api.editStory, 
        loadingMessage: 'Editing with AI...',
        successStatus: 'edited'
      },
      post: { 
        apiCall: api.postToSlack, 
        loadingMessage: 'Posting to Slack...',
        successStatus: 'posted'
      },
      'post-figma': { 
        apiCall: api.postToSlackFigma, 
        loadingMessage: 'Posting to Figma channel...',
        successStatus: 'posted'
      },
    };

    try {
      const currentAction = actionMap[action];
      setMessage(currentAction.loadingMessage);
      
      const response = await currentAction.apiCall(storyId);
      setMessage(response.message);

      // Update the article in local state instead of reloading all news
      updateArticleInState(storyId, { status: currentAction.successStatus });
      
      // If it's an edit action, also update the body if provided in the response
      if (action === 'edit' && response.body) {
        updateArticleInState(storyId, { body: response.body });
      }
    } catch (err: any) {
      const errorMessage = err.message || `An unknown error occurred while performing action: ${action}.`;
      if (errorMessage.includes('Failed to fetch')) {
        setError('Could not connect to the backend. Please ensure the server is running and try again.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setActingArticleId(null);
      // Clear the message after a few seconds
      setTimeout(() => setMessage(null), 5000);
    }
  };

  /**
   * Handles the headline remix action.
   * @param storyId The ID of the target article.
   */
  const handleRemixAction = async (storyId: string) => {
    const article = articles.find(a => a.id === storyId);
    if (!article) return;

    setRemixArticleId(storyId);
    setRemixArticleTitle(article.title);
    setRemixModalOpen(true);
    setIsRemixing(true);
    setRemixOptions([]);

    try {
      const response = await api.remixHeadline(storyId);
      setRemixOptions(response.remixes);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to generate headline remixes.';
      setError(errorMessage);
      setRemixModalOpen(false);
    } finally {
      setIsRemixing(false);
    }
  };

  /**
   * Handles the article scoring action.
   * @param storyId The ID of the target article.
   */
  const handleScoreAction = (storyId: string) => {
    const article = articles.find(a => a.id === storyId);
    if (!article) return;

    setScoringArticle(article);
    setScoringModalOpen(true);
  };

  /**
   * Handles saving updated scores for an article.
   * @param scores The updated scores.
   */
  const handleScoresUpdate = async (scores: { score_relevance: number; score_vibe: number; score_viral: number }) => {
    if (!scoringArticle) return;

    try {
      await api.updateArticleScores(scoringArticle.id, scores);
      
      // Update the article in local state
      updateArticleInState(scoringArticle.id, scores);
      
      setMessage('Article scores updated successfully!');
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update article scores.';
      setError(errorMessage);
    }
  };

  /**
   * Handles saving a custom title for an article.
   * @param customTitle The selected custom title.
   */
  const handleSaveCustomTitle = async (customTitle: string) => {
    if (!remixArticleId) return;

    setIsRemixing(true);
    try {
      await api.saveCustomTitle(remixArticleId, customTitle);
      
      // Update the article in local state
      updateArticleInState(remixArticleId, { custom_title: customTitle });
      
      setMessage('Custom title saved successfully!');
      setRemixModalOpen(false);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to save custom title.';
      setError(errorMessage);
    } finally {
      setIsRemixing(false);
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

  /**
   * Clears all filters and resets to default state.
   */
  const clearAllFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setSourceFilter('all');
    setDateFrom('');
    setDateTo('');
    setAdvancedSearch({
      titleOnly: false,
      bodyOnly: false,
      sourceOnly: false,
    });
  };

  /**
   * Saves current filter state as a preset.
   */
  const saveCurrentPreset = () => {
    const presetName = prompt('Enter a name for this filter preset:');
    if (!presetName) return;

    const newPreset: FilterPreset = {
      id: Date.now().toString(),
      name: presetName,
      filters: {
        searchTerm,
        statusFilter,
        sourceFilter,
        dateFrom,
        dateTo,
        advancedSearch: { ...advancedSearch },
      },
    };

    const updatedPresets = [...filterPresets, newPreset];
    setFilterPresets(updatedPresets);
    saveFilterPresets(updatedPresets);
    setMessage(`Filter preset "${presetName}" saved successfully!`);
  };

  /**
   * Applies a saved filter preset.
   */
  const applyPreset = (preset: FilterPreset) => {
    const { filters } = preset;
    setSearchTerm(filters.searchTerm);
    setStatusFilter(filters.statusFilter);
    setSourceFilter(filters.sourceFilter);
    setDateFrom(filters.dateFrom);
    setDateTo(filters.dateTo);
    setAdvancedSearch(filters.advancedSearch);
    setShowPresets(false);
    setMessage(`Applied filter preset "${preset.name}"`);
  };

  /**
   * Deletes a filter preset.
   */
  const deletePreset = (presetId: string) => {
    const updatedPresets = filterPresets.filter(p => p.id !== presetId);
    setFilterPresets(updatedPresets);
    saveFilterPresets(updatedPresets);
    setMessage('Filter preset deleted successfully!');
  };

  /**
   * Exports filtered articles to JSON.
   */
  const exportFilteredArticles = () => {
    const dataStr = JSON.stringify(filteredArticles, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `filtered-articles-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
    setMessage('Articles exported successfully!');
  };

  /**
   * Filters articles based on search term, status, source, date range, and advanced search options.
   */
  const filteredArticles = articles.filter(article => {
    // Date filtering
    if (dateFrom || dateTo) {
      const articleDate = new Date(article.date);
      if (dateFrom && articleDate < new Date(dateFrom)) return false;
      if (dateTo && articleDate > new Date(dateTo)) return false;
    }

    // Advanced search filtering
    let matchesSearch = !searchTerm;
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      if (advancedSearch.titleOnly) {
        matchesSearch = article.title.toLowerCase().includes(searchLower);
      } else if (advancedSearch.bodyOnly) {
        matchesSearch = article.body.toLowerCase().includes(searchLower);
      } else if (advancedSearch.sourceOnly) {
        matchesSearch = article.source.toLowerCase().includes(searchLower);
      } else {
        // Default: search in all fields
        matchesSearch = 
          article.title.toLowerCase().includes(searchLower) ||
          article.body.toLowerCase().includes(searchLower) ||
          article.source.toLowerCase().includes(searchLower);
      }
    }
    
    const matchesStatus = statusFilter === 'all' || article.status === statusFilter;
    const matchesSource = sourceFilter === 'all' || article.source === sourceFilter;
    
    return matchesSearch && matchesStatus && matchesSource;
  });

  /**
   * Gets unique sources from articles for the filter dropdown.
   */
  const uniqueSources = Array.from(new Set(articles.map(article => article.source))).sort();

  return (
    <div>
      <div className="feed-header">
        <h1>News Feed</h1>
        <div className="header-actions">
          <button onClick={handleIngestNews} disabled={isLoading()}>
            {isLoading('ingesting') ? 'Ingesting...' : (isLoading('loading_feed') ? 'Loading...' : 'Update News')}
          </button>
          <button onClick={exportFilteredArticles} disabled={filteredArticles.length === 0}>
            Export ({filteredArticles.length})
          </button>
        </div>
      </div>

      {/* Filters Section */}
      <div className="filters-section">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search articles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-group">
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="new">New</option>
            <option value="selected">Selected</option>
            <option value="edited">Edited</option>
            <option value="posted">Posted</option>
          </select>
        </div>
        
        <div className="filter-group">
          <select 
            value={sourceFilter} 
            onChange={(e) => setSourceFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Sources</option>
            {uniqueSources.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <button 
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="advanced-toggle-btn"
          >
            {showAdvancedFilters ? 'Hide' : 'Show'} Advanced
          </button>
        </div>

        <div className="filter-group">
          <button 
            onClick={() => setShowPresets(!showPresets)}
            className="presets-toggle-btn"
          >
            {showPresets ? 'Hide' : 'Show'} Presets
          </button>
        </div>

        {/* Add Clear Filters button if any filter is active */}
        {(searchTerm || statusFilter !== 'all' || sourceFilter !== 'all' || dateFrom || dateTo) && (
          <div className="filter-group">
            <button
              onClick={clearAllFilters}
              className="clear-filters-btn"
              type="button"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <div className="advanced-filters">
          <div className="date-filters">
            <div className="filter-group">
                  <label htmlFor="from-date">From Date:</label>
                  <input
                    id="from-date"
                    type="date"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    className="date-input"
                  />
                </div>
                <div className="filter-group">
                  <label htmlFor="to-date">To Date:</label>
                  <input
                    id="to-date"
                    type="date"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    className="date-input"
                  />
                </div>
              </div>
          
          <div className="advanced-search-options">
            <label>Search in:</label>
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={advancedSearch.titleOnly}
                  onChange={(e) => setAdvancedSearch(prev => ({ ...prev, titleOnly: e.target.checked }))}
                />
                Title Only
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={advancedSearch.bodyOnly}
                  onChange={(e) => setAdvancedSearch(prev => ({ ...prev, bodyOnly: e.target.checked }))}
                />
                Body Only
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={advancedSearch.sourceOnly}
                  onChange={(e) => setAdvancedSearch(prev => ({ ...prev, sourceOnly: e.target.checked }))}
                />
                Source Only
              </label>
            </div>
          </div>

          <div className="filter-actions">
            <button onClick={clearAllFilters} className="clear-filters-btn">
              Clear All Filters
            </button>
            <button onClick={saveCurrentPreset} className="save-preset-btn">
              Save as Preset
            </button>
          </div>
        </div>
      )}

      {/* Filter Presets */}
      {showPresets && (
        <div className="filter-presets">
          <h3>Saved Filter Presets</h3>
          {filterPresets.length === 0 ? (
            <p>No saved presets. Create one using the "Save as Preset" button.</p>
          ) : (
            <div className="presets-list">
              {filterPresets.map(preset => (
                <div key={preset.id} className="preset-item">
                  <span className="preset-name">{preset.name}</span>
                  <div className="preset-actions">
                    <button onClick={() => applyPreset(preset)} className="apply-preset-btn">
                      Apply
                    </button>
                    <button onClick={() => deletePreset(preset.id)} className="delete-preset-btn">
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Display error or success messages */}
      {error && <p className="message error">{error}</p>}
      {message && <p className="message success">{message}</p>}
      
      {/* Display a loading message or the list of articles */}
      {isLoading('loading_feed') && articles.length === 0 ? (
        <p>Loading news feed...</p>
      ) : (
        <div className="articles-container">
          {filteredArticles.length === 0 ? (
            <div className="no-results">
              <p>No articles found matching your filters.</p>
              {/* Removed duplicate Clear Filters button here */}
            </div>
          ) : (
            <>
              <div className="results-info">
                Showing {filteredArticles.length} of {articles.length} articles
                {dateFrom || dateTo ? ` (filtered by date)` : ''}
                {advancedSearch.titleOnly || advancedSearch.bodyOnly || advancedSearch.sourceOnly ? ` (advanced search)` : ''}
              </div>
              {filteredArticles.map(article => (
                <ArticleCard 
                  key={article.id} 
                  article={article} 
                  onAction={handleAction}
                  isLoading={isLoading(article.id)}
                />
              ))}
            </>
          )}
        </div>
      )}
      
      {/* Headline Remix Modal */}
      <HeadlineRemixModal
        isOpen={remixModalOpen}
        onClose={() => setRemixModalOpen(false)}
        originalTitle={remixArticleTitle}
        remixes={remixOptions}
        onSelectHeadline={handleSaveCustomTitle}
        isLoading={isRemixing}
      />

      {/* Article Scoring Modal */}
      {scoringModalOpen && scoringArticle && (
        <div className="modal-overlay" onClick={() => setScoringModalOpen(false)}>
          <div className="modal-content scoring-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🎯 Article Scoring</h2>
              <button className="close-btn" onClick={() => setScoringModalOpen(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="article-info">
                <h3>{scoringArticle.title}</h3>
                <p className="article-source">Source: {scoringArticle.source}</p>
              </div>
              <ArticleScoring
                article={scoringArticle}
                onScoresUpdate={handleScoresUpdate}
                isEditable={true}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Feed;
