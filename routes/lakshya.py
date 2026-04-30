from fastapi import status,HTTPException,APIRouter,Depends
from sqlmodel import Session,select
from typing import Annotated

from schemas.lakshya import LakshyaCreate,LakshyaPublic,Lakshya
from schemas.khiladi import Khiladi,KhiladiWithLakshyas
from core.config import get_session

router=APIRouter(tags=["Lakshya"])

@router.post("/khiladi/{username}/lakshyaBanao",response_model=LakshyaPublic)
async def lakshyabanao(username:str,
                       lakshyadata:LakshyaCreate,
                       session:Annotated[Session,Depends(get_session)]):
    statement=select(Khiladi).where(Khiladi.username==username)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta!")
    

    db_laskhya=Lakshya.model_validate(lakshyadata,update={"khiladi_id":db_khiladi.id})
    
    db_laskhya.khiladi_id=db_khiladi.id

    session.add(db_laskhya)
    session.commit()
    session.refresh(db_laskhya)
    return db_laskhya


@router.delete("/khiladi/{username}/{lakshya_id}/deleteLakshya")
async def deletelakshya(username:str,lakshya_id:int,session:Annotated[Session,Depends(get_session)]):
    statement=select(Khiladi).where(Khiladi.username==username)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta!")
    statement2=select(Lakshya).where((Lakshya.id==lakshya_id)& (Lakshya.khiladi_id==db_khiladi.id))
    db_lakshya=session.exec(statement2).first()
    if not db_lakshya:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, tera ye lakshya exist nhi krta")
    
    session.delete(db_lakshya)
    session.commit()
    
    return {"message":f"permananently deleted lakshya with id :{lakshya_id}"}


@router.get("/khiladi/{username}/lakshyas",response_model=KhiladiWithLakshyas,response_model_exclude_unset=True)
async def get_lakshyas(username:str,session:Annotated[Session,Depends(get_session)]):
    statement=select(Khiladi).where(Khiladi.username==username)
    db_khiladi=session.exec(statement).first()
    if not db_khiladi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh khiladi exist nahi karta!")

    return db_khiladi  

