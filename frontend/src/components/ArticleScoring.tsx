import React, { useState, useEffect } from 'react';
import * as api from '../services/api';
import type { Article } from '../types';
import './ArticleScoring.css';

interface ArticleScoringProps {
    article: Article;
    onArticleUpdate: (articleId: string, updates: Partial<Article>) => void;
    isEditable?: boolean;
}

const ArticleScoring: React.FC<ArticleScoringProps> = ({
    article,
    onArticleUpdate,
    isEditable = true
}) => {
    const [scores, setScores] = useState({
        score_relevance: article.score_relevance || 50,
        score_vibe: article.score_vibe || 50,
        score_viral: article.score_viral || 50
    });
    const [isLoading, setIsLoading] = useState(false);
    const [distribution, setDistribution] = useState<any>(null);

    useEffect(() => {
        if (article.id) {
            loadDistribution();
        }
    }, [article.id]);

    const loadDistribution = async () => {
        try {
            const dist = await api.getArticleDistribution(article.id);
            setDistribution(dist.distribution);
        } catch (error) {
            console.error('Failed to load distribution:', error);
        }
    };

    const handleScoreChange = (scoreType: string, value: number) => {
        // Only update local state on slider change
        setScores(prevScores => ({ ...prevScores, [scoreType]: value }));
    };

    const handleAutoScore = async () => {
        setIsLoading(true);
        try {
            const result = await api.scoreArticle(article.id);
            console.log('Auto-score API result:', result); // Diagnostic log

            const updates = {
                ...result.scores,
                ...result.distribution
            };

            // Update local state for immediate UI feedback
            setScores(result.scores);
            setDistribution(result.distribution);
            
            // Update parent component's state
            onArticleUpdate(article.id, updates);

        } catch (error) {
            console.error('Failed to auto-score article:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveScores = async () => {
        setIsLoading(true);
        try {
            const result = await api.updateArticleScores(article.id, scores);
            
            const updates = {
                ...result.scores,
                ...result.distribution
            };

            // Update local state and parent state
            setDistribution(result.distribution);
            onArticleUpdate(article.id, updates);

        } catch (error)
        {
            console.error('Failed to save scores:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return '#28a745'; // Green
        if (score >= 60) return '#ffc107'; // Yellow
        if (score >= 40) return '#fd7e14'; // Orange
        return '#dc3545'; // Red
    };

    const getScoreLabel = (score: number) => {
        if (score >= 90) return '🔥 EXCELLENT';
        if (score >= 80) return '⚡ GREAT';
        if (score >= 70) return '✅ GOOD';
        if (score >= 60) return '🟡 DECENT';
        if (score >= 40) return '🟠 WEAK';
        return '❌ POOR';
    };

    const getChannelIcon = (channel: string) => {
        switch (channel.toLowerCase()) {
            case 'slack': return '💬';
            case 'figma': return '🎨';
            case 'whatsapp': return '📱';
            case 'nft': return '💎';
            case 'manual_review': return '👁️';
            default: return '📢';
        }
    };

    return (
        <div className="article-scoring">
            <div className="scoring-header">
                <h3>🎯 Loud Hawk Scoring</h3>
                <div className="scoring-actions">
                    {isEditable && (
                        <>
                            <button 
                                onClick={handleAutoScore}
                                disabled={isLoading}
                                className="auto-score-btn"
                            >
                                {isLoading ? 'Scoring...' : '🤖 Auto-Score'}
                            </button>
                            <button 
                                onClick={handleSaveScores}
                                disabled={isLoading}
                                className="save-scores-btn"
                            >
                                {isLoading ? 'Saving...' : '💾 Save Scores'}
                            </button>
                        </>
                    )}
                </div>
            </div>

            <div className="scoring-grid">
                {/* Relevance Score */}
                <div className="score-item">
                    <div className="score-header">
                        <span className="score-label">🎯 Relevance</span>
                        <span className="score-value" style={{ color: getScoreColor(scores.score_relevance) }}>
                            {scores.score_relevance}
                        </span>
                    </div>
                    <div className="score-description">
                        {getScoreLabel(scores.score_relevance)}
                    </div>
                    {isEditable && (
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={scores.score_relevance}
                            onChange={(e) => handleScoreChange('score_relevance', parseInt(e.target.value))}
                            className="score-slider"
                            style={{
                                background: `linear-gradient(to right, #dc3545 0%, #fd7e14 40%, #ffc107 60%, #28a745 100%)`
                            }}
                        />
                    )}
                    <div className="score-explanation">
                        Is it useful & impactful for the aviation community?
                    </div>
                </div>

                {/* Vibe Score */}
                <div className="score-item">
                    <div className="score-header">
                        <span className="score-label">🔥 Vibe</span>
                        <span className="score-value" style={{ color: getScoreColor(scores.score_vibe) }}>
                            {scores.score_vibe}
                        </span>
                    </div>
                    <div className="score-description">
                        {getScoreLabel(scores.score_vibe)}
                    </div>
                    {isEditable && (
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={scores.score_vibe}
                            onChange={(e) => handleScoreChange('score_vibe', parseInt(e.target.value))}
                            className="score-slider"
                            style={{
                                background: `linear-gradient(to right, #dc3545 0%, #fd7e14 40%, #ffc107 60%, #28a745 100%)`
                            }}
                        />
                    )}
                    <div className="score-explanation">
                        Does it have the rebellious *Loud Hawk* attitude?
                    </div>
                </div>

                {/* Viral Score */}
                <div className="score-item">
                    <div className="score-header">
                        <span className="score-label">🚀 Virality</span>
                        <span className="score-value" style={{ color: getScoreColor(scores.score_viral) }}>
                            {scores.score_viral}
                        </span>
                    </div>
                    <div className="score-description">
                        {getScoreLabel(scores.score_viral)}
                    </div>
                    {isEditable && (
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={scores.score_viral}
                            onChange={(e) => handleScoreChange('score_viral', parseInt(e.target.value))}
                            className="score-slider"
                            style={{
                                background: `linear-gradient(to right, #dc3545 0%, #fd7e14 40%, #ffc107 60%, #28a745 100%)`
                            }}
                        />
                    )}
                    <div className="score-explanation">
                        Could it spark reactions or go viral on social?
                    </div>
                </div>
            </div>

            {/* Distribution Recommendations */}
            {distribution && (
                <div className="distribution-section">
                    <h4>📡 Distribution Recommendations</h4>
                    <div className="distribution-grid">
                        <div className="distribution-item">
                            <span className="distribution-label">Target Channels:</span>
                            <div className="channel-badges">
                                {distribution.target_channels?.length > 0 ? (
                                    distribution.target_channels.map((channel: string, index: number) => (
                                        <span key={index} className="channel-badge">
                                            {getChannelIcon(channel)} {channel.toUpperCase()}
                                        </span>
                                    ))
                                ) : (
                                    <span className="no-channels">No channels recommended</span>
                                )}
                            </div>
                        </div>
                        
                        <div className="distribution-item">
                            <span className="distribution-label">Auto Post:</span>
                            <span className={`auto-post-status ${distribution.auto_post ? 'enabled' : 'disabled'}`}>
                                {distribution.auto_post ? '✅ Enabled' : '❌ Disabled'}
                            </span>
                        </div>
                        
                        <div className="distribution-item">
                            <span className="distribution-label">Priority:</span>
                            <span className={`priority-badge priority-${distribution.priority}`}>
                                {distribution.priority?.toUpperCase()}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ArticleScoring; 