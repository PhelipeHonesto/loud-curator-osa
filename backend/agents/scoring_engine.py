import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

def score_article(article: Dict[str, Any]) -> Dict[str, int]:
    """
    Score an article on three dimensions for Loud Hawk distribution.
    
    Args:
        article: Article dictionary with title and body
        
    Returns:
        Dictionary with score_relevance, score_vibe, score_viral (0-100)
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            return {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}
        
        client = OpenAI(api_key=api_key)
        
        # Loud Hawk-specific scoring prompt
        prompt = f"""
        You're a Gen Z aviation editor at Loud Hawk, Orange Sunshine Aviation's media engine.
        
        Analyze this aviation article and score it from 0-100 on three dimensions:

        **1. RELEVANCE (0-100)**
        - How useful/important is this for the aviation community?
        - Does it affect pilots, mechanics, enthusiasts, or industry?
        - Is it breaking news, safety info, or industry developments?
        - Higher scores for: safety incidents, regulatory changes, major industry news
        - Lower scores for: generic travel articles, non-aviation content

        **2. VIBE (0-100)**
        - How well does it match Loud Hawk's rebellious, sarcastic, Gen Z tone?
        - Does it have attitude, edge, or controversy potential?
        - Would it fit in a "hot takes" or "spicy aviation news" format?
        - Higher scores for: drama, controversy, irony, corporate BS, pilot stories
        - Lower scores for: corporate PR, boring technical specs, generic news

        **3. VIRALITY (0-100)**
        - How likely is this to be shared, commented on, or go viral?
        - Does it have emotional impact, humor, or shock value?
        - Would people want to share this with their aviation friends?
        - Higher scores for: shocking incidents, funny stories, dramatic events
        - Lower scores for: routine updates, boring announcements

        **ARTICLE TO SCORE:**
        Title: {article.get('title', 'No title')}
        Body: {article.get('body', 'No content')[:800]}...
        Source: {article.get('source', 'Unknown')}

        Respond ONLY with valid JSON in this exact format:
        {{
            "score_relevance": [0-100],
            "score_vibe": [0-100],
            "score_viral": [0-100]
        }}

        No explanations, just the JSON object.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )

        content = response.choices[0].message.content
        if not content:
            logger.error("Empty response from OpenAI")
            return {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}
        
        # Parse JSON response
        try:
            scores = json.loads(content.strip())
            
            # Validate scores are within range
            for key in ['score_relevance', 'score_vibe', 'score_viral']:
                if key not in scores:
                    scores[key] = 50
                else:
                    scores[key] = max(0, min(100, int(scores[key])))
            
            logger.info(f"Scored article '{article.get('title', 'Unknown')}': {scores}")
            return scores
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse scoring response: {e}")
            return {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}
            
    except Exception as e:
        logger.error(f"Error scoring article: {e}")
        return {"score_relevance": 50, "score_vibe": 50, "score_viral": 50}

def decide_distribution(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decide where to distribute an article based on its scores.
    
    Args:
        article: Article with scoring fields
        
    Returns:
        Dictionary with distribution decisions
    """
    relevance = article.get('score_relevance', 50)
    vibe = article.get('score_vibe', 50)
    viral = article.get('score_viral', 50)
    
    # Distribution logic based on Loud Hawk's strategy
    targets = []
    auto_post = False
    
    # High relevance + high vibe = Slack (main channel)
    if relevance >= 75 and vibe >= 70:
        targets.append("slack")
        auto_post = True
    
    # High vibe + high viral = Figma (design team)
    if vibe >= 65 and viral >= 70:
        targets.append("figma")
        if relevance >= 60:
            auto_post = True
    
    # High viral + decent relevance = WhatsApp (community)
    if viral >= 75 and relevance >= 50:
        targets.append("whatsapp")
        if vibe >= 60:
            auto_post = True
    
    # High relevance but low vibe = manual review needed
    if relevance >= 80 and vibe < 50:
        targets.append("manual_review")
        auto_post = False
    
    return {
        "target_channels": targets,
        "auto_post": auto_post,
        "priority": "high" if relevance >= 80 else "medium" if relevance >= 60 else "low"
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