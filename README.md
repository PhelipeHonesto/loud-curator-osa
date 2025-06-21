# OsaCurator: The Orange Sunshine Aviation News Curation App

OsaCurator is a full-stack web application designed to streamline the news curation workflow for an aviation-focused organization. It allows users to ingest news from various sources, select important stories, rewrite them with the help of AI, and post them directly to a Slack channel.

The application features a Python/FastAPI backend that manages data ingestion and workflow logic, and a modern React/TypeScript frontend for a dynamic and responsive user experience.

![OsaCurator Screenshot](https://i.imgur.com/your-screenshot.png) <!-- Replace with a real screenshot URL -->

## ✨ Features

- **Multi-Source Ingestion**: Fetches news from web scrapers (SkyWest press releases) and external APIs (Newsdata.io).
- **Curation Workflow**: A clear, multi-step process for a story: `New` -> `Selected` -> `Edited` -> `Posted`.
- **AI-Powered Editing**: Integrates with the OpenAI API to rewrite and polish news articles.
- **Slack Integration**: Posts curated and edited articles directly to a specified Slack channel using webhooks.
- **Modern UI**: A sleek, responsive, dark-themed interface built with React and TypeScript.
- **Clean Architecture**: The backend is organized with a service-oriented approach, and the frontend uses a component-based structure with a dedicated API service layer.

## 🛠️ Tech Stack

- **Backend**: Python 3, FastAPI, Uvicorn, Requests, BeautifulSoup4, python-dotenv, OpenAI
- **Frontend**: React, TypeScript, Vite
- **Database**: A simple `news.json` file serves as the local database.

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

- Python 3.8+ and `pip`
- Node.js 16+ and `npm` (or `yarn`)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/osacurator.git
cd osacurator
```

### 2. Backend Setup

First, set up and run the Python backend.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required dependencies
pip install -r requirements.txt
```

#### Environment Variables (Backend)

The backend requires API keys for OpenAI and a Slack Webhook URL.

1.  Create a file named `.env` inside the `backend/` directory.
2.  Add the following key-value pairs to the file:

    ```env
    # backend/.env

    # Get from https://platform.openai.com/api-keys
    OPENAI_API_KEY="sk-..."

    # Get from https://api.slack.com/messaging/webhooks
    SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

    # Get from https://newsdata.io/api-key
    NEWSDATA_API_KEY="..."
    ```

#### Running the Backend

With the dependencies and environment variables in place, run the FastAPI server:

```bash
# From the backend/ directory
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`.

---

### 3. Frontend Setup

In a **new terminal window**, set up and run the React frontend.

```bash
# Navigate to the frontend directory from the project root
cd frontend

# Install the required dependencies
npm install
```

#### Running the Frontend

Start the Vite development server:

```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173` (or another port if 5173 is busy). Open this URL in your browser to use OsaCurator.

## ⚙️ Project Structure

```
osacurator/
├── backend/
│   ├── .env            # Backend environment variables (needs to be created)
│   ├── .gitignore
│   ├── agents/         # Modules for fetching news from different sources
│   ├── database.py     # Handles all interactions with news.json
│   ├── main.py         # Main FastAPI application, routes, and logic
│   ├── news.json       # Simple file-based database
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/ # Reusable React components (e.g., ArticleCard)
    │   ├── pages/      # Page components (e.g., Feed, Saved)
    │   ├── services/   # Centralized API call logic (api.ts)
    │   ├── types/      # Shared TypeScript type definitions
    │   ├── App.css     # Global styles
    │   ├── App.tsx     # Main app component with routing
    │   ├── main.tsx    # Application entry point
    │   └── ...
    ├── .gitignore
    ├── index.html
    ├── package.json
    └── ...
```

---

That's it! You should now have a fully functional OsaCurator running locally.

