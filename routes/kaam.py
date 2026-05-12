from fastapi import HTTPException, status, APIRouter, Depends, Query, Form, UploadFile, File, BackgroundTasks
from sqlmodel import select, SQLModel, Session
from typing import Annotated
from datetime import date, timedelta
from schemas.kaam import Kaam, KaamCreate, KaamDifficulty, KaamPublic, KaamStatus, KaamSubmit, calculate_penalty_xp
from core.config import get_session, engine
from core.security import get_current_khiladi
from schemas.khiladi import Khiladi
from schemas.lakshya import Lakshya
from utils.ai_reviewer import evaluate_saboot, process_ai_review_background
import cloudinary
import cloudinary.uploader

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
        print(f" STREAK IGNITED: {db_khiladi.username} started a new streak! +{STREAK_BONUS_XP} XP bonus.")
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


router = APIRouter(tags=["Kaam"], prefix="/kaam")


@router.post("/lakshya/{lakshya_id}", response_model=KaamPublic, status_code=status.HTTP_201_CREATED)
async def create_kaam(lakshya_id: int, kaamdata: KaamCreate, current_khiladi: Annotated[Khiladi, Depends(get_current_khiladi)], session: Annotated[Session, Depends(get_session)]):
    statement = select(Lakshya).where((Lakshya.id == lakshya_id) & (Lakshya.khiladi_id == current_khiladi.id))
    db_lakshya = session.exec(statement).first()
    if not db_lakshya:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bhai yeh lakshya exist nahi karta")
    
    db_kaam = Kaam.model_validate(kaamdata, update={"lakshya_id": lakshya_id})
    db_kaam.penalty_xp = calculate_penalty_xp(db_kaam.difficulty, db_kaam.xp_reward)

    session.add(db_kaam)
    session.commit()
    session.refresh(db_kaam)
    return db_kaam


@router.patch("/{kaam_id}/submit", response_model=KaamPublic)
async def submit_kaam(
    kaam_id: int,
    currentkhiladi: Annotated[Khiladi, Depends(get_current_khiladi)],
    session: Annotated[Session, Depends(get_session)],
    bg_tasks: BackgroundTasks,
    # Form and File dependencies
    saboot_text: str | None = Form(default=None),
    saboot_image: UploadFile | None = File(default=None)
):
    
    statement = select(Kaam).join(Lakshya).where((Kaam.id == kaam_id) & (Lakshya.khiladi_id == currentkhiladi.id))
    db_kaam = session.exec(statement).first()
    
    if not db_kaam: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bhai yeh kaam exist nahi karta")
    
    if db_kaam.status == KaamStatus.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bhai yeh kaam tum already kar chuke ho")
    
    if saboot_text:
        db_kaam.saboot_text = saboot_text
        
    if saboot_image:
        if not saboot_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Bhai, sirf images allowed hain!")
        try:
            # Upload to cloud 
            result = cloudinary.uploader.upload(saboot_image.file, folder="kaamkaaj_saboots")
            # Save the database 
            db_kaam.saboot_image_url = result.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Cloud upload failed. Try again.")
    
    if db_kaam.requires_verification:
        db_kaam.status = KaamStatus.in_review
        bg_tasks.add_task(process_ai_review_background, db_kaam.id, currentkhiladi.id)
    else:
        db_kaam.status = KaamStatus.completed
        
        # --- THE DEBT PAYOFF MATH ---
        currentkhiladi.total_xp += db_kaam.xp_reward
        if currentkhiladi.xp_debt > 0:
            currentkhiladi.xp_debt = max(0, currentkhiladi.xp_debt - db_kaam.xp_reward)
            
        update_streak_on_completion(currentkhiladi)
        
        if currentkhiladi.total_xp < 0:
            currentkhiladi.level = 0
        else:
            currentkhiladi.level = 1 + (currentkhiladi.total_xp // 1000)
            
        session.add(currentkhiladi)
        
    session.add(db_kaam)
    session.commit()
    session.refresh(db_kaam)
    return db_kaam


@router.get("/", response_model=list[KaamPublic])
async def getKaam(currentKhiladi: Annotated[Khiladi, Depends(get_current_khiladi)],
                 session: Annotated[Session, Depends(get_session)],
                 lakshya_id: int | None = Query(default=None, description="Filter tasks by a specific Lakshya"),
                 status_filter: KaamStatus | None = Query(default=None, description=("Filter tasks by status (e.g., pending)"))):
    
    statement = select(Kaam).join(Lakshya).where((Lakshya.khiladi_id == currentKhiladi.id))
    if lakshya_id is not None:
        statement = statement.where(Kaam.lakshya_id == lakshya_id)
    if status_filter is not None:
        statement = statement.where(Kaam.status == status_filter)

    kaams = session.exec(statement).all()
    return kaams
# from fastapi import Query,Path,status,HTTPException,Body,APIRouter,Depends
# from typing import Annotated
# from schemas.kaam import KaamCreate



# router=APIRouter(
#     prefix="/kaam",
#     tags=["Kaam"]
#     )
# class  KaamPaginationParams:
#      def __init__(self,skip:int=0,limit:int=10):
#          self.skip=skip
#          self.limit=limit


# def extract_search_query(q: str | None = None):
#     if q:
#         return q.lower()
#     return None

# def get_advanced_filters(
#     pagination: Annotated[KaamPaginationParams, Depends()],
#     search_keyword: Annotated[str | None, Depends(extract_search_query)]
# ):
#     return {
#         "skip": pagination.skip,
#         "limit": pagination.limit,
#         "search": search_keyword
#     }

# @router.get("/difficulty/{level}")
# async def get_difficulty_wise_kaam(level:difficultylevel):
#     if level==difficultylevel.hard:
#         return {"message":"most dangerous quest"}
#     elif level==difficultylevel.medium:
#         return {"message":"medium quest"}
#     else:
#         return {"message":"cake walk quest"}
    
# @router.get("/search")
# async def searchKaam(query:Annotated[str|None, Query(min_length=3,max_length=20,pattern="^[a-zA-Z0-9 ]+$")]=None):
#     if query is None:
#         return {"message":"Please provide kaam name for the search "}
#     else:
#         return {"message":f"searching for {query} !"}
    

# @router.get("/filter/tags")
# async def filterkaam(tags:Annotated[list[str]|None,Query(alias="kaam-tags",title="Kaam Tags",description="Filter your Kaam by multiple categories (e.g., study, workout).")]=None):
#     if not tags:
#         return {"message":"provide tags for filtering"}
#     else:
#         return {"message":f"filtering kaam with respect to {tags}"}



# @router.get("/{kaam_id}")
# async def get_kaam(kaam_id:Annotated[int,Path(ge=1,le=1000)],xp_multiply:Annotated[float,Query(ge=0,le=5.0)]=None):
#     if xp_multiply is None:
#         message="None"
#     else:
#         message=xp_multiply
#     if kaam_id>100:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh kaam exist nahi karta")
#     return {
#         "kaam_id": kaam_id,
#         "kaam_name": f"Defeat the Goblin King (ID: {kaam_id})",
#         "xp_reward_muliplier": message,
#         "status": "Incomplete"
#     }


# @router.get("/")
# async def list_kaams(filters:Annotated[dict,Depends(get_advanced_filters)]):
#     return {
#         "message":f"Fetching quests from the database...",
#         "filters_applied":filters
#     }

# @router.post("/")
# async def create_kaam(kaam:Kaam_Create):
#     print("Server log:quest is being created")
#     return{
#         "message":f"your quest named:{kaam.name} and worth {kaam.xp_reward}xp is created!",
#         "quest_data":kaam
#     }
    

# @router.put("/{kaam_id}")
# async def updatekaam(kaam_id:int,kaam_data:KaamUpdate,notify_khiladi:bool=False):
#     return{
#         "message":"Successfully updated",
#         "updated_id":kaam_id,
#         "updated kaam":kaam_data,
#         "notify_khildai":notify_khiladi
#     }

# @router.put("/{kaam_id}/submit")
# async def submit_kaam(
#     kaam_id:int,
#     resolution:KaamResolution,
#     proof:Saboot,
#     rating:Annotated[int,Body(ge=1,le=5)]=None
#     ):
#     return {
#         "message":"Kaam submitted successfully",
#         "submitted_kaam_id":kaam_id,
#         "resolution":resolution,
#         "Saboot":proof
#     }

# @router.post("/Advanced/create")
# async def createDetailedKaam(
#     deatiledkaamdata:KammDetailedCreate
# ):
#  return {"message":"detailed kaam created",
#         "kaam_data":deatiledkaamdata}

