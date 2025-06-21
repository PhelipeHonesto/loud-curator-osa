from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from typing import List, Dict

# Local imports
from . import database
from .agents.aviation_pages_reader import fetch_skywest_news
from .agents.newsdata_agent import fetch_newsdata_news

# --- Application Setup ---
# Load environment variables once at startup
load_dotenv(dotenv_path=database.DB_FILE.parent / ".env")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencies ---
def get_article_dependency(story_id: str) -> Dict:
    """FastAPI dependency to fetch an article by ID or raise a 404 error."""
    article = database.find_news_by_id(story_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID '{story_id}' not found.",
        )
    return article

# --- API Endpoints ---
@app.get("/", summary="Root endpoint for health check")
def read_root():
    return {"status": "ok"}

@app.get("/news", summary="Get all news articles", response_model=List[Dict])
def get_news():
    """Returns a list of all news articles, sorted by date descending."""
    news = database.get_all_news()
    return sorted(news, key=lambda x: x.get("date", ""), reverse=True)

@app.post("/ingest", summary="Ingest new articles from all sources")
def ingest_news():
    """Fetches new articles from all agents, filters out duplicates, and saves them."""
    existing_news = database.get_all_news()
    existing_links = {article["link"] for article in existing_news}

    new_articles = fetch_skywest_news() + fetch_newsdata_news()
    
    unique_new_articles = [
        article for article in new_articles if article["link"] not in existing_links
    ]

    combined_news = unique_new_articles + existing_news
    database.save_all_news(combined_news)

    return {"message": f"Successfully ingested {len(unique_new_articles)} new articles."}

@app.post("/select/{story_id}", summary="Select a story for editing")
def select_story(article: Dict = Depends(get_article_dependency)):
    """Marks an article's status as 'selected'."""
    all_news = database.get_all_news()
    for item in all_news:
        if item["id"] == article["id"]:
            item["status"] = "selected"
            break
    database.save_all_news(all_news)
    return {"message": f"Story {article['id']} has been selected."}

@app.post("/edit/{story_id}", summary="Rewrite a story using AI")
def edit_story(article: Dict = Depends(get_article_dependency)):
    """Sends a selected article to the OpenAI API for rewriting."""
    if article["status"] not in ["selected", "edited"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'selected' or 'edited' before editing.",
        )
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Rewrite the following news article for a general audience. Keep it concise, informative, and engaging. \n\nTitle: {article['title']}\n\nArticle: {article['body']}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
        )
        edited_body = chat_completion.choices[0].message.content
        
        if not edited_body:
            raise HTTPException(status_code=500, detail="AI failed to generate content.")

        all_news = database.get_all_news()
        for item in all_news:
            if item["id"] == article["id"]:
                item["body"] = edited_body
                item["status"] = "edited"
                break
        database.save_all_news(all_news)

        return {"message": f"Story {article['id']} has been edited by AI."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred with the OpenAI API: {e}",
        )

@app.post("/slack/{story_id}", summary="Post a story to Slack")
def post_to_slack(article: Dict = Depends(get_article_dependency)):
    """Formats and sends an edited article to a Slack channel via webhook."""
    if article["status"] != "edited":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'edited' before posting to Slack.",
        )

    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SLACK_WEBHOOK_URL not found in environment.",
        )

    slack_payload = {
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f":newspaper: {article['title']}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": article.get('body', 'No content available.')}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Source: *{article['source']}* | <{article['link']}|Read Original>"}]},
        ]
    }
    
    try:
        response = requests.post(slack_webhook_url, json=slack_payload)
        response.raise_for_status()

        all_news = database.get_all_news()
        for item in all_news:
            if item["id"] == article["id"]:
                item["status"] = "posted"
                break
        database.save_all_news(all_news)

        return {"message": f"Story {article['id']} has been posted to Slack."}

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post to Slack: {e}",
        )
