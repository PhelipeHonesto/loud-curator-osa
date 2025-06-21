import { useState, useEffect } from 'react';
import './Settings.css';

interface Settings {
  NEWSDATA_API_KEY: string;
  OPENAI_API_KEY: string;
  SLACK_WEBHOOK_URL: string;
  SLACK_WEBHOOK_FIGMA_URL: string;
  GROUNDNEWS_API_KEY: string;
}

const Settings = () => {
  const [settings, setSettings] = useState<Settings>({
    NEWSDATA_API_KEY: '',
    OPENAI_API_KEY: '',
    SLACK_WEBHOOK_URL: '',
    SLACK_WEBHOOK_FIGMA_URL: '',
    GROUNDNEWS_API_KEY: '',
  });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  };

  const handleInputChange = (key: keyof Settings, value: string) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    setMessage(null);
    setError(null);

    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        setMessage('Settings saved successfully!');
        setTimeout(() => setMessage(null), 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to save settings');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestConnection = async (type: 'newsdata' | 'openai' | 'slack' | 'groundnews') => {
    setIsLoading(true);
    setMessage(null);
    setError(null);

    try {
      const response = await fetch(`/api/test-connection/${type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ apiKey: settings[`${type.toUpperCase()}_API_KEY` as keyof Settings] }),
      });

      if (response.ok) {
        setMessage(`${type.toUpperCase()} connection test successful!`);
      } else {
        const errorData = await response.json();
        setError(`${type.toUpperCase()} connection failed: ${errorData.detail}`);
      }
    } catch (err) {
      setError(`Failed to test ${type.toUpperCase()} connection`);
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setMessage(null);
        setError(null);
      }, 5000);
    }
  };

  const maskApiKey = (key: string) => {
    if (!key) return '';
    if (key.length <= 8) return '*'.repeat(key.length);
    return key.substring(0, 4) + '*'.repeat(key.length - 8) + key.substring(key.length - 4);
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>Settings</h1>
        <p>Configure your API keys and integration settings</p>
      </div>

      {error && <div className="message error">{error}</div>}
      {message && <div className="message success">{message}</div>}

      <div className="settings-section">
        <h2>API Configuration</h2>
        
        <div className="setting-group">
          <label htmlFor="newsdata-key">NewsData.io API Key</label>
          <div className="input-group">
            <input
              id="newsdata-key"
              type="password"
              value={settings.NEWSDATA_API_KEY}
              onChange={(e) => handleInputChange('NEWSDATA_API_KEY', e.target.value)}
              placeholder="Enter your NewsData.io API key"
            />
            <button
              onClick={() => handleTestConnection('newsdata')}
              disabled={isLoading || !settings.NEWSDATA_API_KEY}
              className="test-btn"
            >
              Test
            </button>
          </div>
          <small>Used to fetch aviation news from various sources</small>
        </div>

        <div className="setting-group">
          <label htmlFor="openai-key">OpenAI API Key</label>
          <div className="input-group">
            <input
              id="openai-key"
              type="password"
              value={settings.OPENAI_API_KEY}
              onChange={(e) => handleInputChange('OPENAI_API_KEY', e.target.value)}
              placeholder="Enter your OpenAI API key"
            />
            <button
              onClick={() => handleTestConnection('openai')}
              disabled={isLoading || !settings.OPENAI_API_KEY}
              className="test-btn"
            >
              Test
            </button>
          </div>
          <small>Used for AI-powered article editing and rewriting</small>
        </div>

        <div className="setting-group">
          <label htmlFor="groundnews-key">Ground News API Key (Optional)</label>
          <div className="input-group">
            <input
              id="groundnews-key"
              type="password"
              value={settings.GROUNDNEWS_API_KEY}
              onChange={(e) => handleInputChange('GROUNDNEWS_API_KEY', e.target.value)}
              placeholder="Enter your Ground News API key (optional)"
            />
            <button
              onClick={() => handleTestConnection('groundnews')}
              disabled={isLoading || !settings.GROUNDNEWS_API_KEY}
              className="test-btn"
            >
              Test
            </button>
          </div>
          <small>Used to fetch balanced news coverage with fact-checking</small>
        </div>
      </div>

      <div className="settings-section">
        <h2>Slack Integration</h2>
        
        <div className="setting-group">
          <label htmlFor="slack-webhook">Default Slack Webhook URL</label>
          <div className="input-group">
            <input
              id="slack-webhook"
              type="url"
              value={settings.SLACK_WEBHOOK_URL}
              onChange={(e) => handleInputChange('SLACK_WEBHOOK_URL', e.target.value)}
              placeholder="https://hooks.slack.com/services/..."
            />
            <button
              onClick={() => handleTestConnection('slack')}
              disabled={isLoading || !settings.SLACK_WEBHOOK_URL}
              className="test-btn"
            >
              Test
            </button>
          </div>
          <small>Webhook URL for posting curated articles to your default Slack channel</small>
        </div>

        <div className="setting-group">
          <label htmlFor="slack-figma-webhook">Figma Slack Webhook URL</label>
          <div className="input-group">
            <input
              id="slack-figma-webhook"
              type="url"
              value={settings.SLACK_WEBHOOK_FIGMA_URL}
              onChange={(e) => handleInputChange('SLACK_WEBHOOK_FIGMA_URL', e.target.value)}
              placeholder="https://hooks.slack.com/services/..."
            />
            <button
              onClick={() => handleTestConnection('slack')}
              disabled={isLoading || !settings.SLACK_WEBHOOK_FIGMA_URL}
              className="test-btn"
            >
              Test
            </button>
          </div>
          <small>Webhook URL for posting articles in Figma-compatible format</small>
        </div>
      </div>

      <div className="settings-section">
        <h2>Current Configuration</h2>
        <div className="config-preview">
          <div className="config-item">
            <strong>NewsData.io:</strong> {settings.NEWSDATA_API_KEY ? '✓ Configured' : '✗ Not configured'}
          </div>
          <div className="config-item">
            <strong>OpenAI:</strong> {settings.OPENAI_API_KEY ? '✓ Configured' : '✗ Not configured'}
          </div>
          <div className="config-item">
            <strong>Ground News:</strong> {settings.GROUNDNEWS_API_KEY ? '✓ Configured' : '✗ Not configured'}
          </div>
          <div className="config-item">
            <strong>Slack Default:</strong> {settings.SLACK_WEBHOOK_URL ? '✓ Configured' : '✗ Not configured'}
          </div>
          <div className="config-item">
            <strong>Slack Figma:</strong> {settings.SLACK_WEBHOOK_FIGMA_URL ? '✓ Configured' : '✗ Not configured'}
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button
          onClick={handleSave}
          disabled={isLoading}
          className="save-btn"
        >
          {isLoading ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      <div className="settings-help">
        <h3>Need Help?</h3>
        <ul>
          <li><strong>NewsData.io:</strong> Get your API key from <a href="https://newsdata.io" target="_blank" rel="noopener noreferrer">newsdata.io</a></li>
          <li><strong>OpenAI:</strong> Get your API key from <a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer">platform.openai.com</a></li>
          <li><strong>Ground News:</strong> Get your API key from <a href="https://ground.news" target="_blank" rel="noopener noreferrer">ground.news</a></li>
          <li><strong>Slack Webhooks:</strong> Create webhooks in your Slack workspace settings</li>
        </ul>
      </div>
    </div>
  );
};

export default Settings;
