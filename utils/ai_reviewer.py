import os
import httpx
from datetime import datetime, date, timedelta
from google import genai
from google.genai import types
from pydantic import BaseModel
from sqlmodel import select, Session
from core.config import engine
from schemas.khiladi import Khiladi
from schemas.kaam import Kaam, KaamStatus, calculate_penalty_xp

STREAK_BONUS_XP = 50

def update_streak_on_completion(db_khiladi: Khiladi):
    """Ignite Mechanic: Update streak when a Kaam is completed and pay off debt."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    def award_streak_xp():
        db_khiladi.total_xp += STREAK_BONUS_XP
        if db_khiladi.xp_debt > 0:
            db_khiladi.xp_debt = max(0, db_khiladi.xp_debt - STREAK_BONUS_XP)

    if db_khiladi.last_streak_date is None:
        db_khiladi.current_streak = 1
        db_khiladi.longest_streak = 1
        db_khiladi.last_streak_date = today
        award_streak_xp()
        print(f"STREAK IGNITED: {db_khiladi.username} started a new streak! +{STREAK_BONUS_XP} XP bonus.")
        return True

    last_date = db_khiladi.last_streak_date

    if last_date == today:
        return False

    if last_date == yesterday:
        db_khiladi.current_streak += 1
        db_khiladi.last_streak_date = today
        award_streak_xp()

        if db_khiladi.current_streak > db_khiladi.longest_streak:
            db_khiladi.longest_streak = db_khiladi.current_streak

        print(f"STREAK EXTENDED: {db_khiladi.username} streak is now {db_khiladi.current_streak}! +{STREAK_BONUS_XP} XP bonus.")
        return True

    db_khiladi.current_streak = 1
    db_khiladi.longest_streak = max(db_khiladi.longest_streak, 1)
    db_khiladi.last_streak_date = today
    award_streak_xp()
    print(f"STREAK RESTARTED: {db_khiladi.username} lost their streak but started fresh. +{STREAK_BONUS_XP} XP bonus.")
    return True

class GameMasterJudgement(BaseModel):
    is_approved: bool
    feedback: str

def evaluate_saboot(kaam_title: str, kaam_description: str | None, saboot_text: str | None, saboot_image_url: str | None) -> GameMasterJudgement:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are the Game Master of 'KaamKaaj', a hardcore RPG productivity and accountability platform. 
    You are a strict but fair judge. You despise laziness and fake submissions, but you reward genuine effort.

    Your task is to verify if a Khiladi (user) has successfully completed their assigned Kaam (task).

    [CONTEXT]
    Kaam Title: "{kaam_title}"
    Kaam Description: "{kaam_description or 'No description provided'}"
    Text Proof (Saboot): "{saboot_text or 'No text proof provided'}"

    [EVALUATION RULES]
    1. Analyze the provided Text Proof and Image Proof (if attached) against the Kaam Title and Description.
    2. If the goal requires physical proof (e.g., "Run 5km") and only vague text is provided without an image, you MUST reject it.
    3. If the goal is mental/digital (e.g., "Read 10 pages") and the text proof contains specific, convincing details, you may approve it.
    4. If you detect any attempt to cheat, reject it immediately and provide harsh (but professional) feedback.
    """
    contents = [prompt]
    if saboot_image_url:
        try:
            response = httpx.get(saboot_image_url)
            if response.status_code == 200:
                image_part = types.Part.from_bytes(
                    data=response.content,
                    mime_type=response.headers.get('Content-Type', 'image/jpeg')
                )
                contents.append(image_part)
        except Exception as e:
            print(f"Failed to fetch image for AI Vision: {e}")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GameMasterJudgement, 
                temperature=0.0, 
            ),
        )
        return response.parsed
    except Exception as e:
        print(f"Game Master API Error: {e}")
        return GameMasterJudgement(
            is_approved=False,
            feedback="The Game Master encountered a magical disturbance. Please try submitting again."
        )

def process_ai_review_background(kaam_id: int, khiladi_id: int):
    with Session(engine) as session:
        statement = select(Kaam).where(Kaam.id == kaam_id)
        db_kaam = session.exec(statement).first()
        
        khiladi_statement = select(Khiladi).where(Khiladi.id == khiladi_id)
        db_khiladi = session.exec(khiladi_statement).first()

        if not db_kaam or not db_khiladi:
            return 
        
        print(f"Game Master is analyzing Kaam ID: {kaam_id}...")
        judgment = evaluate_saboot(
            kaam_title=db_kaam.title,
            kaam_description=db_kaam.description,
            saboot_text=db_kaam.saboot_text,
            saboot_image_url=db_kaam.saboot_image_url
        )

        db_kaam.ai_feedback = judgment.feedback
        
        if judgment.is_approved:
            db_kaam.status = KaamStatus.completed
            
            # --- THE DEBT PAYOFF MATH ---
            db_khiladi.total_xp += db_kaam.xp_reward
            if db_khiladi.xp_debt > 0:
                db_khiladi.xp_debt = max(0, db_khiladi.xp_debt - db_kaam.xp_reward)
            
            # Streak bonus will also pay off debt if applicable
            update_streak_on_completion(db_khiladi)
            
            if db_khiladi.total_xp < 0:
                db_khiladi.level = 0
            else:
                db_khiladi.level = 1 + (db_khiladi.total_xp // 1000)
                
            print(f"Game Master APPROVED! Granted {db_kaam.xp_reward} XP.")
            
        else:
            db_kaam.status = KaamStatus.rejected
            db_kaam.has_been_penalized = True
            db_kaam.failed_at = datetime.utcnow()
            
            penalty = calculate_penalty_xp(db_kaam.difficulty, db_kaam.xp_reward)
            db_kaam.penalty_xp = penalty
            db_khiladi.total_xp -= penalty
            db_khiladi.xp_debt += penalty
            
            if db_khiladi.total_xp < 0:
                db_khiladi.level = 0
            else:
                db_khiladi.level = 1 + (db_khiladi.total_xp // 1000)
            
            print(f"Game Master REJECTED! Penalty: {penalty} XP deducted. Total XP: {db_khiladi.total_xp}")

        session.add(db_kaam)
        session.add(db_khiladi)
        session.commit()