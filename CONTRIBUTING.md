# Contributing to Loud Curator

Thank you for your interest in contributing to Loud Curator! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Adding New News Agents](#adding-new-news-agents)
- [Frontend Development](#frontend-development)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Getting Started

Before contributing, please:

1. Read the main [README.md](README.md) to understand the project
2. Set up the development environment (see below)
3. Familiarize yourself with the codebase structure
4. Check existing issues and pull requests to avoid duplicates

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd loud-curator-osa
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Environment Configuration:**
   Create a `.env` file in the `backend` directory:
   ```env
   NEWSDATA_API_KEY="your_newsdata.io_api_key"
   OPENAI_API_KEY="your_openai_api_key"
   SLACK_WEBHOOK_URL="your_slack_webhook_url"
   SLACK_WEBHOOK_FIGMA_URL="your_figma_slack_webhook_url"
   GROUNDNEWS_API_KEY="your_groundnews_api_key"  # Optional
   ```

5. **Start Development Servers:**
   ```bash
   # From project root
   ./start_dev.sh
   ```

## Project Structure

```
loud-curator-osa/
├── backend/                 # FastAPI backend
│   ├── agents/             # News ingestion modules
│   │   ├── aviation_pages_reader.py
│   │   ├── newsdata_agent.py
│   │   ├── institutional_reader.py
│   │   └── groundnews_agent.py
│   ├── main.py             # FastAPI application
│   ├── database_sqlite.py  # Data persistence
│   └── requirements.txt
├── frontend/               # React/Vite frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service layer
│   │   └── types/          # TypeScript type definitions
│   └── package.json
└── README.md
```

## Adding New News Agents

News agents are modules in the `backend/agents/` directory that fetch articles from different sources. Here's how to create a new agent:

### 1. Create the Agent File

Create a new Python file in `backend/agents/` (e.g., `my_news_agent.py`):

```python
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv


def fetch_my_news() -> List[Dict[str, Any]]:
    """
    Fetches news from your custom source.
    Returns a list of article dictionaries.
    """
    # Load environment variables
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    # Your API key (if needed)
    API_KEY = os.getenv("MY_API_KEY")
    if not API_KEY:
        print("Error: MY_API_KEY not found in .env file.")
        return []

    # Fetch data from your source
    url = "https://api.yoursource.com/news"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        for item in data.get("articles", []):
            article = {
                "id": str(uuid.uuid4()),
                "title": item.get("title"),
                "date": item.get("publishedAt", datetime.now().isoformat()),
                "body": item.get("description", ""),
                "link": item.get("url"),
                "source": "Your Source Name",
                "status": "new",
            }
            
            # Ensure required fields are present
            if article["title"] and article["link"]:
                articles.append(article)
                
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from your source: {e}")
        return []
    except ValueError:
        print("Error: Could not decode JSON response")
        return []
```

### 2. Update main.py

Add your agent to the imports and ingest function in `backend/main.py`:

```python
# Add import
from agents.my_news_agent import fetch_my_news

# Add to ingest_news function
try:
    print("Fetching news from your source...")
    my_articles = fetch_my_news()
    print(f"Found {len(my_articles)} articles from your source.")
    all_new_articles.extend(my_articles)
except Exception as e:
    print(f"Error fetching news from your source: {e}")
```

### 3. Update Requirements (if needed)

If your agent requires new dependencies, add them to `backend/requirements.txt`.

### Agent Requirements

Each agent should:

- Return a list of dictionaries with the following structure:
  ```python
  {
      "id": str,           # Unique identifier
      "title": str,        # Article title
      "date": str,         # ISO format date
      "body": str,         # Article content/description
      "link": str,         # URL to original article
      "source": str,       # Source name
      "status": str,       # Always "new" for new articles
  }
  ```
- Handle errors gracefully and return empty lists on failure
- Use environment variables for API keys
- Include proper logging/print statements for debugging

## Frontend Development

### Component Structure

- **Components** (`src/components/`): Reusable UI components
- **Pages** (`src/pages/`): Page-level components
- **Services** (`src/services/`): API communication layer
- **Types** (`src/types/`): TypeScript type definitions

### Adding New Features

1. **Create new components** in `src/components/`
2. **Add new pages** in `src/pages/`
3. **Update routing** in `src/App.tsx` if needed
4. **Add API methods** in `src/services/api.ts`
5. **Define types** in `src/types/index.ts`

### State Management

The app uses React's built-in state management. For complex state, consider:
- React Context for global state
- React Query for server state
- Zustand for simple global state

## Testing

### Backend Testing

Create tests in a `tests/` directory:

```python
# tests/test_my_agent.py
import pytest
from agents.my_news_agent import fetch_my_news

def test_fetch_my_news():
    articles = fetch_my_news()
    assert isinstance(articles, list)
    # Add more specific tests
```

Run tests:
```bash
cd backend
pytest tests/
```

### Frontend Testing

Use React Testing Library:

```typescript
// src/components/__tests__/ArticleCard.test.tsx
import { render, screen } from '@testing-library/react';
import ArticleCard from '../ArticleCard';

test('renders article title', () => {
  const article = {
    id: '1',
    title: 'Test Article',
    // ... other fields
  };
  
  render(<ArticleCard article={article} onAction={() => {}} />);
  expect(screen.getByText('Test Article')).toBeInTheDocument();
});
```

Run tests:
```bash
cd frontend
npm test
```

## Code Style

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Keep functions focused and small
- Use meaningful variable names

### TypeScript/React (Frontend)

- Use TypeScript for all new code
- Follow ESLint rules
- Use functional components with hooks
- Prefer composition over inheritance
- Use meaningful component and variable names

### General

- Write clear commit messages
- Add comments for complex logic
- Keep functions and components focused
- Test your changes

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Test your changes:**
   - Run backend tests: `cd backend && pytest`
   - Run frontend tests: `cd frontend && npm test`
   - Test manually in development

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new news agent for X source"
   ```

5. **Push and create a PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Guidelines:**
   - Use descriptive titles
   - Include a summary of changes
   - Reference related issues
   - Add screenshots for UI changes
   - Ensure all tests pass

## Reporting Issues

When reporting issues, please include:

1. **Environment details:**
   - OS and version
   - Python version
   - Node.js version
   - Browser (for frontend issues)

2. **Steps to reproduce:**
   - Clear, step-by-step instructions
   - Expected vs actual behavior

3. **Error messages:**
   - Full error logs
   - Stack traces

4. **Additional context:**
   - Screenshots (if applicable)
   - Configuration details
   - Recent changes that might have caused the issue

## Getting Help

- Check existing issues and discussions
- Review the codebase and documentation
- Ask questions in issues or discussions
- Join the project's community channels

Thank you for contributing to Loud Curator! 🚀 