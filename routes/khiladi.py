from fastapi import APIRouter,status,Depends,HTTPException
from typing import Annotated
from sqlmodel import Session,select
from core.config import get_session
from schemas.khiladi import Khiladi,KhiladiCreate,KhiladiProfile,KhiladiPublic,KhiladiUpdate

router=APIRouter(prefix="/khiladi",tags=["Khiladi"])

@router.post("/Register",response_model=KhiladiPublic,status_code=status.HTTP_201_CREATED)
async def register_khiladi(
    khiladidata:KhiladiCreate,
    session:Annotated[Session,Depends(get_session)]
):  
    db_khiladi=Khiladi.model_validate(khiladidata) # You are taking the Pydantic JSON- 
                                                  #-struct (khiladidata), allocating a brand new SQLAlchemy Table Struct (db_khiladi) in your RAM (the Heap),
                                                  # - and copying the variables over.
                                                  #At this exact microsecond, your new struct has an id that is None (a Null Pointer), 
                                                  ##and it does NOT have a level yet, because the database hasn't generated them.
    session.add(db_khiladi) # step 1 stage the change (initate the on the fly sql)
    session.commit() # step 2 execute sql and save in db
    session.refresh(db_khiladi) # refresh,i.e dynamically update updated values(eg id goes from null to 1 ) into my db_khiladi struct sitting in RAM."
                                # so that python or fastapi is also gets updated of the change and when returning db_khildai, conversion is smooth
    return db_khiladi

@router.get("/{username}/profile",response_model=KhiladiProfile,response_model_exclude_unset=True)
async def getKhiladiProfile(
    username:str,
    session:Annotated[Session,Depends(get_session)]
):
    statement=select(Khiladi).where(Khiladi.username==username)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta")
    return db_khiladi

@router.patch("/{username}/updateProfile",response_model=KhiladiProfile)
async def update_user_profile(username:str,khiladi_new_data:KhiladiUpdate,
                              session:Annotated[Session,Depends(get_session)]):
    statement=select(Khiladi).where(Khiladi.username==username)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta!")
    
    data_to_be_updated=khiladi_new_data.model_dump(exclude_unset=True)
    db_khiladi.sqlmodel_update(data_to_be_updated)
    session.add(db_khiladi)
    session.commit()
    session.refresh(db_khiladi)
    return db_khiladi

@router.delete("/{username}/deleteProfile")
async def deleteKhiladi(username:str,session:Annotated[Session,Depends(get_session)]):
    statement=select(Khiladi).where(Khiladi.username==username)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta!")
    
    session.delete(db_khiladi)
    session.commit()
    return {"message":f"permananently deleted {username}"}
    

@router.get("/{khiladi_id}/kaam")
async def list_khiladi_kaam(khiladi_id:int,city:str,isurgent:bool,search_keyword:str|None=None):
    response_message=f"getting kaam of khiladi with id :{khiladi_id} in {city} "
    if isurgent:
        response_message+=" WARNING: Bhai, jaldi karo! (Prioritizing URGENT Kaam!)"
    if search_keyword:
        response_message+=f" filtering the kaams with {search_keyword}"
    return{
        "message":response_message,
        "filters_applied":{
            "city":city,
            "isurgent":isurgent,
            "search_keyword":search_keyword
        }
    }