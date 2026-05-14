import os
import hashlib
from datetime import datetime, date
from google import genai
from google.genai import types
from pydantic import BaseModel

class DailyMessageAIResponse(BaseModel):
    message: str
    message_type: str
    mood: str

def generate_daily_message(
    username: str, 
    current_streak: int, 
    level: int, 
    tasks_completed_today: int,
    overdue_tasks: int,
    in_shadow_realm: bool
) -> DailyMessageAIResponse:
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    shadow_realm_str = "User is currently in the Shadow Realm." if in_shadow_realm else "User is not in the Shadow Realm."
    
    prompt = f"""
    You are KaamKaaj's AI Accountability Companion - "The Voice of the Grind".
    
    [USER STATS]
    Name: {username}
    Streak: {current_streak} days
    Level: {level}
    Tasks Completed Today: {tasks_completed_today}
    Overdue Tasks: {overdue_tasks}
    Shadow Realm Status: {shadow_realm_str}
    
    [YOUR PERSONALITY]
    - Direct, never sugarcoat, but always constructive
    - Use the user's name when possible
    - Reference their specific stats (streak, level, recent activity)
    - Match the intensity to their current state
    - Be memorable - use specific language, not generic phrases

    [TONE MAPPING]
    - Streak > 7 days + high activity → Proud, challenge them
    - Streak broken + overdue tasks → Warning, wake-up call
    - Consistent good performance → Praise, motivate to push further
    - Low activity → Welcome, motivate to start
    - Shadow Realm → Serious, help them escape

    [RULES]
    1. Keep messages 1-3 sentences, punchy.
    2. NEVER use generic quotes.
    3. Use their actual data (e.g. "Your {current_streak}-day streak..." not "Your streak...").
    4. End with energy - call to action or challenge.
    5. The message_type should be one of: motivate, challenge, roast, encourage, praise, warn, focus.
    6. The mood should be one of: energetic, calm, urgent, playful, serious.
    """
    
    contents = [prompt]
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DailyMessageAIResponse, 
                temperature=0.7, 
            ),
        )
        return response.parsed
    except Exception as e:
        print(f"Daily Message AI Error: {e}")
        # Fallback
        return DailyMessageAIResponse(
            message=f"The grind doesn't wait, {username}. Start with ONE Kaam today.",
            message_type="focus",
            mood="serious"
        )
