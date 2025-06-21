# OsaCurator

This repository contains a very small demonstration project with a FastAPI backend and a Vite/React frontend. The backend exposes two endpoints:

- `/news` – returns the contents of `news.json`
- `/ingest` – fetches news from two example agents and appends them to `news.json`

The frontend is a simple React app that displays the articles and has a button to trigger ingestion.

## Running locally

1. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```
   > Note: the container used for testing does not have network access, so this step will fail in Codex.

2. **Start the FastAPI server**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Install front‑end dependencies**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Again, this requires network access.

