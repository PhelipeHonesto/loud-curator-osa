import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

def score_and_route_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score an article and decide distribution channels for Loud Hawk.
    Returns a dict with scores and target channels.
    """
    # --- AI Scoring ---
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            scores = {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}
        else:
            client = OpenAI(api_key=api_key)
            prompt = f"""
You're an editorial assistant for a rebellious Gen Z aviation brand.\n\nAnalyze this news article and give 3 scores (0–100):\n\n1. **Relevance** – Is it useful, timely, and impactful for the aviation community?\n2. **Vibe** – Does it match our *Loud Hawk* tone (sarcastic, rebellious, punchy)?\n3. **Virality** – Could it spread on social, spark strong reactions, or memes?\n\nRespond in JSON like:\n{{\n  \"score_relevance\": 0–100,\n  \"score_vibe\": 0–100,\n  \"score_viral\": 0–100\n}}\n\nArticle:\nTitle: {article.get('title', 'No title')}\nBody: {article.get('body', 'No content')[:800]}\n"""
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            content = response.choices[0].message.content
            if not content:
                logger.error("Empty response from OpenAI")
                scores = {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}
            else:
                try:
                    scores = json.loads(content.strip())
                    for key in ["score_relevance", "score_vibe", "score_viral"]:
                        if key not in scores:
                            scores[key] = 50
                        else:
                            scores[key] = max(0, min(100, int(scores[key])))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse scoring response: {e}")
                    scores = {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}
    except Exception as e:
        logger.error(f"Error scoring article: {e}")
        scores = {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}

    # --- Distribution Logic ---
    r = scores["score_relevance"]
    v = scores["score_vibe"]
    vir = scores["score_viral"]
    channels = []
    if r >= 85 and v >= 85:
        channels = ["slack", "whatsapp", "figma", "nft"]
    elif v >= 80 and vir >= 75:
        channels = ["whatsapp", "figma"]
    elif r >= 70 and vir >= 80:
        channels = ["slack", "figma"]
    elif vir >= 90:
        channels = ["figma"]
    elif v >= 60:
        channels = ["whatsapp"]
    # Priority and auto_post
    priority = "high" if r >= 85 else "medium" if r >= 70 else "low"
    auto_post = True if r >= 85 or (v >= 80 and vir >= 75) else False
    return {
        **scores,
        "target_channels": channels,
        "priority": priority,
        "auto_post": auto_post
    }

def decide_distribution(article: Dict[str, Any]) -> Dict[str, Any]:
    result = score_and_route_article(article)
    return {
        "target_channels": result["target_channels"],
        "priority": result["priority"],
        "auto_post": result["auto_post"]
    }

def get_score_description(score: int, score_type: str) -> str:
    """
    Get a human-readable description of a score.
    
    Args:
        score: Score value (0-100)
        score_type: Type of score (relevance, vibe, viral)
        
    Returns:
        Description string
    """
    if score >= 90:
        return f"🔥 {score_type.title()} - EXCELLENT"
    elif score >= 80:
        return f"⚡ {score_type.title()} - GREAT"
    elif score >= 70:
        return f"✅ {score_type.title()} - GOOD"
    elif score >= 60:
        return f"🟡 {score_type.title()} - DECENT"
    elif score >= 40:
        return f"🟠 {score_type.title()} - WEAK"
    else:
        return f"❌ {score_type.title()} - POOR"

def analyze_article_tone(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the tone and style of an article for Loud Hawk compatibility.
    
    Args:
        article: Article to analyze
        
    Returns:
        Tone analysis results
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"tone": "neutral", "style_match": 50, "recommendations": []}
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        You're analyzing an article for Loud Hawk, a Gen Z aviation media brand.
        
        Analyze this article's tone and style:
        
        Title: {article.get('title', 'No title')}
        Content: {article.get('body', 'No content')[:600]}...
        
        Rate from 0-100 how well it matches Loud Hawk's style:
        - Rebellious, sarcastic, Gen Z voice
        - Calls out corporate BS
        - Celebrates pilot culture
        - Has attitude and edge
        
        Also identify:
        1. Primary tone (corporate, neutral, rebellious, dramatic, etc.)
        2. Key themes that could be emphasized
        3. Potential angles for Loud Hawk treatment
        
        Respond in JSON:
        {{
            "style_match": [0-100],
            "tone": "string",
            "themes": ["theme1", "theme2"],
            "loud_hawk_angle": "suggested angle for Loud Hawk treatment"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        if not content:
            return {"tone": "neutral", "style_match": 50, "recommendations": []}
        
        try:
            analysis = json.loads(content.strip())
            return analysis
        except json.JSONDecodeError:
            return {"tone": "neutral", "style_match": 50, "recommendations": []}
            
    except Exception as e:
        logger.error(f"Error analyzing article tone: {e}")
        return {"tone": "neutral", "style_match": 50, "recommendations": []} 