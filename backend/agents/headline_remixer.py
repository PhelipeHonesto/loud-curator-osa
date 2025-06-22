import os
from openai import OpenAI
from typing import List
import logging

logger = logging.getLogger(__name__)

def remix_headline(title: str, body: str) -> List[str]:
    """
    Generate 3 creative Loud Hawk-style headline variations.
    
    Args:
        title: Original headline
        body: Article content for context
        
    Returns:
        List of 3 remixed headlines
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            return []
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        You're a rebellious Gen Z aviation editor with a sharp, sarcastic voice.

        Original headline: "{title}"
        Context: {body[:500]}...

        Create 3 bold, punchy, sarcastic or emotional headline variations in Loud Hawk style.
        Make them:
        - Attention-grabbing and impactful
        - Slightly rebellious or ironic when appropriate
        - Professional but with attitude
        - No more than 80 characters each

        Return exactly 3 headlines, one per line, no numbering or bullets.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=150
        )

        content = response.choices[0].message.content
        if not content:
            logger.error("Empty response from OpenAI")
            return [f"🔥 {title}", f"💥 {title}", f"⚡ {title}"]
            
        content = content.strip()
        headlines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Ensure we have exactly 3 headlines
        if len(headlines) < 3:
            # Pad with variations if we don't have enough
            while len(headlines) < 3:
                headlines.append(f"Remix {len(headlines) + 1}: {title}")
        elif len(headlines) > 3:
            # Take only the first 3
            headlines = headlines[:3]
        
        logger.info(f"Generated {len(headlines)} headline remixes for: {title}")
        return headlines
        
    except Exception as e:
        logger.error(f"Error generating headline remixes: {e}")
        # Return fallback headlines
        return [
            f"🔥 {title}",
            f"💥 {title}",
            f"⚡ {title}"
        ]

def analyze_headline_style(title: str) -> str:
    """
    Analyze the style of a headline to determine if it needs remixing.
    
    Args:
        title: Headline to analyze
        
    Returns:
        Style classification: "boring", "clickbait", "professional", "good"
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "unknown"
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        Analyze this aviation headline and classify its style:

        Headline: "{title}"

        Choose one:
        - boring (dull, corporate, generic)
        - clickbait (overly sensational, misleading)
        - professional (good balance, informative)
        - good (already engaging, well-written)

        Respond with one word only.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )

        content = response.choices[0].message.content
        if not content:
            logger.error("Empty response from OpenAI for style analysis")
            return "unknown"
            
        style = content.strip().lower()
        return style
        
    except Exception as e:
        logger.error(f"Error analyzing headline style: {e}")
        return "unknown" 