import React, { useState } from 'react';
import './HeadlineRemixModal.css';

interface HeadlineRemixModalProps {
    isOpen: boolean;
    onClose: () => void;
    originalTitle: string;
    remixes: string[];
    onSelectHeadline: (headline: string) => void;
    isLoading: boolean;
}

const HeadlineRemixModal: React.FC<HeadlineRemixModalProps> = ({
    isOpen,
    onClose,
    originalTitle,
    remixes,
    onSelectHeadline,
    isLoading
}) => {
    const [selectedHeadline, setSelectedHeadline] = useState<string>('');

    if (!isOpen) return null;

    const handleSelect = (headline: string) => {
        setSelectedHeadline(headline);
    };

    const handleSave = () => {
        if (selectedHeadline) {
            onSelectHeadline(selectedHeadline);
            onClose();
            setSelectedHeadline('');
        }
    };

    const handleClose = () => {
        onClose();
        setSelectedHeadline('');
    };

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>🎛️ Headline Remix Generator</h2>
                    <button className="close-btn" onClick={handleClose}>×</button>
                </div>

                <div className="modal-body">
                    <div className="original-title-section">
                        <h3>Original Headline:</h3>
                        <p className="original-title">{originalTitle}</p>
                    </div>

                    <div className="remixes-section">
                        <h3>Choose Your Remix:</h3>
                        {isLoading ? (
                            <div className="loading-remixes">
                                <div className="spinner"></div>
                                <p>Generating creative headlines...</p>
                            </div>
                        ) : (
                            <div className="remix-options">
                                {remixes.map((headline, index) => (
                                    <div
                                        key={index}
                                        className={`remix-option ${selectedHeadline === headline ? 'selected' : ''}`}
                                        onClick={() => handleSelect(headline)}
                                    >
                                        <div className="remix-number">#{index + 1}</div>
                                        <div className="remix-text">{headline}</div>
                                        {selectedHeadline === headline && (
                                            <div className="selected-indicator">✓</div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="modal-footer">
                    <button 
                        className="cancel-btn" 
                        onClick={handleClose}
                        disabled={isLoading}
                    >
                        Cancel
                    </button>
                    <button 
                        className="save-btn" 
                        onClick={handleSave}
                        disabled={!selectedHeadline || isLoading}
                    >
                        {isLoading ? 'Saving...' : 'Save Custom Title'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default HeadlineRemixModal; 