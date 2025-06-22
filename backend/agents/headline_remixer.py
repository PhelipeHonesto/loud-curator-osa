import os
from openai import OpenAI
from typing import List
import logging
import asyncio

logger = logging.getLogger(__name__)

class HeadlineRemixer:
    """
    Handles all interactions with the OpenAI API for remixing headlines.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Headline remixing will use default values.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    async def remix_headline(self, title: str, body: str) -> List[str]:
        """
        Generate 3 creative Loud Hawk-style headline variations.
        
        Args:
            title: Original headline
            body: Article content for context
            
        Returns:
            List of 3 remixed headlines
        """
        if not self.client:
            return [f"🔥 {title}", f"💥 {title}", f"⚡ {title}"]

        prompt = self._create_remix_prompt(title, body)

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=150,
            )
            content = response.choices[0].message.content or ""
            headlines = [line.strip() for line in content.strip().split('\n') if line.strip()]

            # Ensure exactly 3 headlines
            if len(headlines) > 3:
                return headlines[:3]
            while len(headlines) < 3:
                headlines.append(f"Remix {len(headlines) + 1}: {title}")
            
            logger.info(f"Generated {len(headlines)} headline remixes for: {title}")
            return headlines

        except Exception as e:
            logger.error(f"Error generating headline remixes for '{title}': {e}", exc_info=True)
            return [f"🔥 {title}", f"💥 {title}", f"⚡ {title}"]

    def _create_remix_prompt(self, title: str, body: str) -> str:
        """Creates the prompt for the headline remixing API call."""
        return f"""
You're a rebellious Gen Z aviation editor with a sharp, sarcastic voice.
Original headline: "{title}"
Context: {body[:500]}...
Create 3 bold, punchy, sarcastic or emotional headline variations.
Make them attention-grabbing and no more than 80 characters each.
Return exactly 3 headlines, one per line, no numbering or bullets.
"""

# Singleton instance for the application to use
headline_remixer = HeadlineRemixer()

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