import { useEffect, useState, useCallback } from 'react';
import './App.css';

interface Article {
  id: string;
  title: string;
  date: string;
  body: string;
  link: string;
  source: string;
  status: string;
}

function App() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchNews = useCallback(() => {
    setIsLoading(true);
    fetch('http://localhost:8000/news')
      .then(response => response.json())
      .then(data => {
        // Sort articles by date, newest first
        const sortedData = data.sort((a: Article, b: Article) => 
          new Date(b.date).getTime() - new Date(a.date).getTime()
        );
        setArticles(sortedData);
      })
      .catch(error => {
        console.error('Error fetching news:', error)
        setMessage('Could not load news.');
      })
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  const handleIngestNews = () => {
    setIsLoading(true);
    setMessage('Ingesting new articles...');
    fetch('http://localhost:8000/ingest', { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        setMessage(data.message || 'Ingestion complete!');
        fetchNews(); // Refresh the news list
      })
      .catch(error => {
        console.error('Error ingesting news:', error);
        setMessage('Ingestion failed.');
      })
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>OsaCurator News</h1>
        <button onClick={handleIngestNews} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Update News'}
        </button>
        {message && <p className="message">{message}</p>}
      </header>
      <main>
        <div className="articles-container">
          {articles.map(article => (
            <div key={article.id} className="article-card">
              <h2>{article.title}</h2>
              <p>{article.body}</p>
              <a href={article.link} target="_blank" rel="noopener noreferrer">
                Read more
              </a>
              <div className="source">Source: {article.source}</div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default App;
