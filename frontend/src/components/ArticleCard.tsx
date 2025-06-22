import type { Article } from '../types';

type ActionType = 'select' | 'edit' | 'post' | 'post-figma' | 'remix' | 'score';

interface ArticleCardProps {
    article: Article;
    onAction: (action: ActionType, storyId: string) => void;
    isLoading: boolean;
}

const ArticleCard = ({ article, onAction, isLoading }: ArticleCardProps) => {
    const getStatusTag = (status: string) => {
        switch (status) {
            case 'selected':
                return { text: 'SELECTED', color: '#f17500' };
            case 'edited':
                return { text: 'EDITED', color: '#0a4bb6' };
            case 'posted':
                return { text: 'POSTED', color: '#28a745' };
            default:
                return { text: 'NEW', color: '#6c757d' };
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return '#28a745';
        if (score >= 60) return '#ffc107';
        if (score >= 40) return '#fd7e14';
        return '#dc3545';
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return '#dc3545';
            case 'medium': return '#ffc107';
            case 'low': return '#6c757d';
            default: return '#6c757d';
        }
    };

    const statusTag = getStatusTag(article.status);
    const formattedDate = new Date(article.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    // Display custom title if available, otherwise show original title
    const displayTitle = article.custom_title || article.title;

    return (
        <div className="article-card">
            {/* Top Section */}
            <div className="card-top">
                <div className="tag-chip" style={{ backgroundColor: statusTag.color }}>
                    {statusTag.text}
                </div>
                <div className="date-source">
                    <span className="date">{formattedDate}</span>
                    <span className="source">{article.source}</span>
                </div>
            </div>

            {/* Middle Section */}
            <div className="card-middle">
                <h2 className="article-title">
                    {displayTitle}
                    {article.custom_title && (
                        <span className="custom-title-indicator"> ✨</span>
                    )}
                </h2>
                <p className="article-summary">
                    {article.body
                        ? (article.body.length > 200 ? `${article.body.substring(0, 200)}...` : article.body)
                        : 'No summary available.'
                    }
                </p>

                {/* Scoring Display */}
                {(article.score_relevance || article.score_vibe || article.score_viral) && (
                    <div className="scoring-preview">
                        <div className="scoring-scores">
                            {article.score_relevance && (
                                <span className="score-badge" style={{ color: getScoreColor(article.score_relevance) }}>
                                    📊 {article.score_relevance}
                                </span>
                            )}
                            {article.score_vibe && (
                                <span className="score-badge" style={{ color: getScoreColor(article.score_vibe) }}>
                                    🔥 {article.score_vibe}
                                </span>
                            )}
                            {article.score_viral && (
                                <span className="score-badge" style={{ color: getScoreColor(article.score_viral) }}>
                                    🚀 {article.score_viral}
                                </span>
                            )}
                        </div>
                        
                        {article.priority && (
                            <span 
                                className="priority-indicator" 
                                style={{ backgroundColor: getPriorityColor(article.priority) }}
                            >
                                {article.priority.toUpperCase()}
                            </span>
                        )}
                        
                        {article.target_channels && article.target_channels.length > 0 && (
                            <div className="target-channels">
                                {article.target_channels.map((channel, index) => (
                                    <span key={index} className="channel-indicator">
                                        {channel === 'slack' && '💬'}
                                        {channel === 'figma' && '🎨'}
                                        {channel === 'whatsapp' && '📱'}
                                        {channel === 'manual_review' && '👁️'}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Bottom Section */}
            <div className="card-bottom">
                <div className="card-actions">
                    <a 
                        href={article.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="read-more-btn"
                    >
                        🔗 Read More
                    </a>
                    
                    <div className="action-buttons">
                        {/* Remix button - always available */}
                        <button 
                            onClick={() => onAction('remix', article.id)}
                            disabled={isLoading}
                            className="action-btn remix-btn"
                        >
                            {isLoading ? 'Remixing...' : '🎛️ Remix Headline'}
                        </button>

                        {/* Score button - always available */}
                        <button 
                            onClick={() => onAction('score', article.id)}
                            disabled={isLoading}
                            className="action-btn score-btn"
                        >
                            {isLoading ? 'Scoring...' : '🎯 Score Article'}
                        </button>

                        {article.status === 'new' && (
                            <button 
                                onClick={() => onAction('select', article.id)}
                                className="action-btn select-btn"
                            >
                                Select Story
                            </button>
                        )}
                        {article.status === 'selected' && (
                            <button 
                                onClick={() => onAction('edit', article.id)} 
                                disabled={isLoading}
                                className="action-btn edit-btn"
                            >
                                {isLoading ? 'Editing...' : 'Edit with AI'}
                            </button>
                        )}
                        {article.status === 'edited' && (
                            <>
                                <button 
                                    onClick={() => onAction('edit', article.id)} 
                                    disabled={isLoading}
                                    className="action-btn reedit-btn"
                                >
                                    {isLoading ? 'Editing...' : 'Re-edit'}
                                </button>
                                <button 
                                    onClick={() => onAction('post', article.id)} 
                                    disabled={isLoading}
                                    className="action-btn post-btn"
                                >
                                    {isLoading ? 'Posting...' : '📤 Send to Slack'}
                                </button>
                                <button 
                                    onClick={() => onAction('post-figma', article.id)} 
                                    disabled={isLoading}
                                    className="action-btn post-figma-btn"
                                >
                                    {isLoading ? 'Posting...' : '🪄 Send Figma Format'}
                                </button>
                            </>
                        )}
                        {article.status === 'posted' && (
                            <button 
                                onClick={() => onAction('select', article.id)} 
                                disabled={isLoading}
                                className="action-btn rewrite-btn"
                            >
                                Rewrite Story
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ArticleCard;
