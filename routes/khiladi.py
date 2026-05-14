from fastapi import APIRouter,status,Depends,HTTPException,BackgroundTasks,Request
from typing import Annotated
from sqlmodel import Session,select
from core.config import get_session
from core.security import get_hashed_password,get_current_khiladi,check_password
from schemas.khiladi import Khiladi,KhiladiCreate,KhiladiProfile,KhiladiPublic,KhiladiUpdate,VerifyOtp,ResendOtpRequest,DeleteProfile,ForgotPasswordRequest,ResetPasswordRequest
from utils.email import send_otp_email
import time,secrets
from datetime import datetime,timezone,timedelta
from core.limiter import limiter

router=APIRouter(prefix="/khiladi",tags=["Khiladi"])

# @router.post("/Register",response_model=KhiladiPublic,status_code=status.HTTP_201_CREATED)
# async def register_khiladi(
#     khiladidata:KhiladiCreate,
#     session:Annotated[Session,Depends(get_session)]
# ):  
#     db_khiladi=Khiladi.model_validate(khiladidata) # You are taking the Pydantic JSON- 
#                                                   #-struct (khiladidata), allocating a brand new SQLAlchemy Table Struct (db_khiladi) in your RAM (the Heap),
#                                                   # - and copying the variables over.
#                                                   #At this exact microsecond, your new struct has an id that is None (a Null Pointer), 
#                                                   ##and it does NOT have a level yet, because the database hasn't generated them.
#     session.add(db_khiladi) # step 1 stage the change (initate the on the fly sql)
#     session.commit() # step 2 execute sql and save in db
#     session.refresh(db_khiladi) # refresh,i.e dynamically update updated values(eg id goes from null to 1 ) into my db_khiladi struct sitting in RAM."
#                                 # so that python or fastapi is also gets updated of the change and when returning db_khildai, conversion is smooth
#     return db_khiladi
#[ THIS ABOVE CODE WAS JUST FOR PHASE 1 LEARNING PHASE, WITHOUT THE SECURITY FEATURES]

@router.post("Register/",response_model=KhiladiPublic,status_code=status.HTTP_201_CREATED)
async def register_khiladi(khiladidata:KhiladiCreate,session:Annotated[Session,Depends(get_session)],
                           bg_tasks:BackgroundTasks):
    statement=select(Khiladi).where(Khiladi.email==khiladidata.email)
    existinguser=session.exec(statement).first()
    if existinguser:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bhai, ye email pehle se registered hai!"
        )
    
    hashed_pw=get_hashed_password(khiladidata.password)
    khiladi_dict=khiladidata.model_dump(exclude={"password"})
    
    cryptic_otp="".join(secrets.choice("0123456789") for _ in range(6))
    expiration_time=datetime.now(timezone.utc)+timedelta(minutes=10)

    db_khiladi=Khiladi(**khiladi_dict,hashed_password=hashed_pw,otp_code=cryptic_otp,otp_expires_at=expiration_time) # **(upacks the dictionary fields as The Khiladi database class expects you to pass arguments exactly like this:-
                                                                 #Khiladi(username="suleman", email="s@mail.com", hashed_password="...") )
    session.add(db_khiladi)
    session.commit()
    session.refresh(db_khiladi)

    bg_tasks.add_task(send_otp_email,db_khiladi.email,db_khiladi.otp_code)
    
    return db_khiladi






# @router.get("/{username}/profile",response_model=KhiladiProfile,response_model_exclude_unset=True)
# async def getKhiladiProfile(
#     username:str,
#     session:Annotated[Session,Depends(get_session)]
# ):
#     statement=select(Khiladi).where(Khiladi.username==username)
#     db_khiladi=session.exec(statement).first()
#     if not db_khiladi:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta")
#     return db_khiladi

# Notice the URL is just /me now!
@router.get("/me/profile", response_model=KhiladiPublic)
async def get_my_profile(
    # THE LOCK: Before this function runs, FastAPI executes get_current_khiladi.
    # If the token is missing or fake, it throws a 401 and stops execution.
    # If it's valid, it passes the exact Khiladi database object into this variable.
    current_user: Khiladi = Depends(get_current_khiladi)
):
    # Because the dependency already fetched the user from the database,
    # we literally just have to return it!
    return current_user


@router.patch("/me/updateProfile",response_model=KhiladiProfile)
async def update_user_profile(khiladi:Annotated[Khiladi,Depends(get_current_khiladi)],khiladi_new_data:KhiladiUpdate,
                              session:Annotated[Session,Depends(get_session)]):
    
    data_to_be_updated=khiladi_new_data.model_dump(exclude_unset=True)
    if "password" in data_to_be_updated:
        user_pw=data_to_be_updated.pop("password")
        hashedpw=get_hashed_password(user_pw)
        data_to_be_updated.update({"hashed_password":hashedpw})
    
    khiladi.sqlmodel_update(data_to_be_updated)
    session.add(khiladi)
    session.commit()
    session.refresh(khiladi)
    return khiladi

@router.delete("/me/deleteProfile")
async def deleteKhiladi(user_password:DeleteProfile,khiladi:Annotated[Khiladi,Depends(get_current_khiladi)],session:Annotated[Session,Depends(get_session)]):
    if not check_password(user_password.password,khiladi.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Galat password, Account can't be deleted")
    session.delete(khiladi)
    session.commit()
    return {"message":f"permananently deleted"}
    

@router.post("/verify-otp",status_code=status.HTTP_200_OK)
async def verifyotp(otpData:VerifyOtp,session:Annotated[Session,Depends(get_session)]):
    statement=select(Khiladi).where(Khiladi.email==otpData.email)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bhai ye khiladi email exist nahi krti!"
        )
    if db_khiladi.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bhai, tu pehle hi verify kar chuka hai"
        )
    

    if  otpData.user_otp!=db_khiladi.otp_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Verification code"
            )
    currenttime=datetime.now(timezone.utc).replace(tzinfo=None)

    if not db_khiladi.otp_expires_at or currenttime>db_khiladi.otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bhai code ye  expire ho chuka hai, request a new one!"
        )
    db_khiladi.is_verified=True
    db_khiladi.otp_code=None
    db_khiladi.otp_expires_at=None

    session.add(db_khiladi)
    session.commit()
    session.refresh(db_khiladi)
    return {"message": "Account successfully verified. Welcome to KaamKaaj!"}
 





@router.post("/resendOtp/")
@limiter.limit("3/minute")
async def resend_otp(
    request:Request,
    otprequest: ResendOtpRequest, 
    bg_tasks: BackgroundTasks, 
    session: Annotated[Session, Depends(get_session)]
):
    
    statement = select(Khiladi).where(Khiladi.email == otprequest.email)
    db_khiladi = session.exec(statement).first()
    
    if not db_khiladi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bhai ye khiladi email exist nahi karti!"
        )
        
    if db_khiladi.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bhai, tu pehle hi verify kar chuka hai"
        )
    
    # 2. Anti-Spam (Fixed Timezone & Math Logic)
    # We use naive UTC time consistently to avoid timezone offset crashes
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if db_khiladi.otp_expires_at:
        # Step A: Strip timezone info from DB object just in case SQLModel added it back
        db_expiry = db_khiladi.otp_expires_at.replace(tzinfo=None)
        
        # Step B: Reverse engineer the exact moment the OTP was created
        generation_time = db_expiry - timedelta(minutes=10)
        
        # Step C: Calculate how many seconds have passed since they clicked the button
        seconds_passed = (now - generation_time).total_seconds()
        
        # Step D: If it has been less than 60 seconds, trigger the shield.
        # (We also check > 0 to ensure no weird negative time travel bugs)
        if 0 <= seconds_passed < 60:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Thoda sabar kar bhai. Please wait {int(60 - seconds_passed)} seconds before requesting a new OTP."
            )

    # 3. Generate New OTP
    new_otp = "".join(secrets.choice("0123456789") for _ in range(6))
    
    # IMPORTANT: Save the new expiry exactly the same way (Naive UTC)
    db_khiladi.otp_code = new_otp
    db_khiladi.otp_expires_at = now + timedelta(minutes=10)

    session.add(db_khiladi)
    session.commit()
    session.refresh(db_khiladi)
    
    
    bg_tasks.add_task(send_otp_email, db_khiladi.email, db_khiladi.otp_code)
    
    return {"message": "Naya OTP bhej diya gaya hai. Apna email check karo!"}

@router.get("/daily-message")
async def get_daily_message(
    current_khiladi: Khiladi = Depends(get_current_khiladi),
    session: Session = Depends(get_session)
):
    from datetime import date
    from schemas.daily_message import DailyMessage, DailyMessageResponse
    from utils.daily_message_ai import generate_daily_message
    from schemas.lakshya import Lakshya
    from schemas.kaam import Kaam
    from sqlalchemy.orm import selectinload
    
    today = date.today()
    statement = select(DailyMessage).where(
        DailyMessage.khiladi_id == current_khiladi.id,
        DailyMessage.shown_at == today
    )
    existing_message = session.exec(statement).first()
    
    if existing_message:
        return DailyMessageResponse(
            message=existing_message.message,
            message_type=existing_message.message_type,
            mood=existing_message.mood,
            is_new=False,
            refresh_available_at=datetime.utcnow() + timedelta(days=1)
        )
        
    from routes.dashboard import get_shadow_realm_status
    in_shadow_realm, _ = get_shadow_realm_status(current_khiladi.total_xp)
    
    khiladi_statement = (
        select(Khiladi)
        .where(Khiladi.id == current_khiladi.id)
        .options(
            selectinload(Khiladi.lakshyas).selectinload(Lakshya.kaams)
        )
    )
    db_khiladi = session.exec(khiladi_statement).first()
    
    tasks_completed_today = 0
    overdue_tasks = 0
    now = datetime.now()
    
    for lak in db_khiladi.lakshyas:
        for kaam in lak.kaams:
            if kaam.status == "completed":
                if kaam.deadline and kaam.deadline.date() == today:
                    tasks_completed_today += 1
            elif kaam.status != "completed":
                if kaam.deadline and kaam.deadline < now:
                    overdue_tasks += 1

    ai_response = generate_daily_message(
        username=current_khiladi.username,
        current_streak=current_khiladi.current_streak,
        level=current_khiladi.level,
        tasks_completed_today=tasks_completed_today,
        overdue_tasks=overdue_tasks,
        in_shadow_realm=in_shadow_realm
    )
    
    new_message = DailyMessage(
        khiladi_id=current_khiladi.id,
        message=ai_response.message,
        message_type=ai_response.message_type,
        mood=ai_response.mood,
        shown_at=today
    )
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    
    return DailyMessageResponse(
        message=new_message.message,
        message_type=new_message.message_type,
        mood=new_message.mood,
        is_new=True,
        refresh_available_at=datetime.utcnow() + timedelta(days=1)
    )


@router.post("/forgot-password")
@limiter.limit("3/minute") # Protect against spamming emails
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    bg_tasks: BackgroundTasks,
    session: Annotated[Session, Depends(get_session)]
):
    statement = select(Khiladi).where(Khiladi.email == payload.email)
    db_khiladi = session.exec(statement).first()

    # Even if user doesn't exist, we usually return a generic message 
    # to prevent "Email Enumeration" attacks (hackers guessing emails).
    if not db_khiladi:
        return {"message": "Agar ye email registered hai, toh OTP bhej diya gaya hai."}

    # Generate new OTP (Reusing your logic)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    new_otp = "".join(secrets.choice("0123456789") for _ in range(6))
    
    db_khiladi.otp_code = new_otp
    db_khiladi.otp_expires_at = now + timedelta(minutes=10)

    session.add(db_khiladi)
    session.commit()
    session.refresh(db_khiladi)

    # Send email in background
    bg_tasks.add_task(send_otp_email, db_khiladi.email, db_khiladi.otp_code)

    return {"message": "Agar ye email registered hai, toh OTP bhej diya gaya hai."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    payload: ResetPasswordRequest,
    session: Annotated[Session, Depends(get_session)]
):
    statement = select(Khiladi).where(Khiladi.email == payload.email)
    db_khiladi = session.exec(statement).first()

    if not db_khiladi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bhai ye khiladi email exist nahi karti!"
        )

    # 1. Verify OTP exactly like you did in /verify-otp
    if payload.user_otp != db_khiladi.otp_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Galat OTP!"
        )
        
    currenttime = datetime.now(timezone.utc).replace(tzinfo=None)
    if not db_khiladi.otp_expires_at or currenttime > db_khiladi.otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bhai ye code expire ho chuka hai, request a new one!"
        )

    # 2. OTP is valid! Now hash the new password and update
    hashed_pw = get_hashed_password(payload.new_password)
    db_khiladi.hashed_password = hashed_pw
    
    # 3. Clean up the OTP so it can't be reused
    db_khiladi.otp_code = None
    db_khiladi.otp_expires_at = None

    session.add(db_khiladi)
    session.commit()
    
    return {"message": "Mubarak ho! Password successfully change ho gaya hai. Aap ab login kar sakte hain."}