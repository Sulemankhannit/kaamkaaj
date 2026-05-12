import asyncio
from datetime import datetime, date, timedelta
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from core.config import engine
from schemas.khiladi import Khiladi
from schemas.kaam import Kaam, KaamStatus, calculate_penalty_xp
from schemas.lakshya import Lakshya

REAPER_INTERVAL_SECONDS = 300

async def run_reaper():
    """Background sweeper that penalizes users for missed deadlines and checks streaks."""
    print("💀 The Reaper is awake and watching...")
    while True:
        try:
            # Running standard synchronous database operations
            reap_deadline_victims()
            extinguish_streaks()
        except Exception as e:
            print(f"⚠️ REAPER ENCOUNTERED AN ERROR: {e}")
        
        # We MUST use await here so the background loop doesn't freeze FastAPI
        await asyncio.sleep(REAPER_INTERVAL_SECONDS)

def extinguish_streaks():
    """Extinguish Mechanic: Check for broken streaks and apply freeze logic."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    with Session(engine) as session:
        # 1. Fetch all khiladis with active streaks
        statement = select(Khiladi).where(Khiladi.current_streak > 0)
        all_khiladis = session.exec(statement).all()
        
        for khiladi in all_khiladis:
            if khiladi.last_streak_date is None:
                continue
            
            # If they haven't updated their streak since before yesterday
            if khiladi.last_streak_date < yesterday:
                if khiladi.streak_freezes > 0:
                    khiladi.streak_freezes -= 1
                    khiladi.last_streak_date = yesterday # Use a freeze to save them
                    session.add(khiladi)
                    print(f"❄️ STREAK FROZEN: {khiladi.username} used a freeze! Left: {khiladi.streak_freezes}")
                else:
                    old_streak = khiladi.current_streak
                    khiladi.current_streak = 0
                    khiladi.last_streak_date = None
                    session.add(khiladi)
                    print(f"🔥 STREAK EXTINGUISHED: {khiladi.username} lost a {old_streak}-day streak!")
        
        session.commit()

def reap_deadline_victims():
    """Check for overdue tasks and apply penalties."""
    with Session(engine) as session:
        now = datetime.utcnow()
        
        # 2. Join tables and load relationships synchronously
        statement = (
            select(Kaam)
            .join(Lakshya)
            .join(Khiladi)
            .where(
                Kaam.deadline != None,
                Kaam.deadline < now,
                Kaam.status.in_([KaamStatus.pending, KaamStatus.in_review]),
                Kaam.has_been_penalized == False
            )
            .options(selectinload(Kaam.lakshya).selectinload(Lakshya.khiladi))
        )
        
        overdue_kaams = session.exec(statement).all()

        if not overdue_kaams:
            return

        for kaam in overdue_kaams:
            # We already have the Khiladi loaded via selectinload
            khiladi = kaam.lakshya.khiladi
            
            penalty = calculate_penalty_xp(kaam.difficulty, kaam.xp_reward)
            
            kaam.status = KaamStatus.rejected
            kaam.has_been_penalized = True
            kaam.penalty_xp = penalty
            kaam.failed_at = now
            kaam.ai_feedback = f"DEADLINE REAPER: Missed deadline on {kaam.deadline}."

            khiladi.total_xp -= penalty
            khiladi.xp_debt += penalty
            
            # Level Logic
            khiladi.level = max(0, 1 + (khiladi.total_xp // 1000))

            session.add(kaam)
            session.add(khiladi)
            print(f"💀 REAPER: Penalized {khiladi.username} {penalty} XP for '{kaam.title}'")

        session.commit()