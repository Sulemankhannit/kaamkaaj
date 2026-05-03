from fastapi import status,HTTPException,APIRouter,Depends
from sqlmodel import Session,select
from typing import Annotated

from schemas.lakshya import LakshyaCreate,LakshyaPublic,Lakshya
from schemas.khiladi import Khiladi,KhiladiWithLakshyas
from core.config import get_session
from core.security import get_current_khiladi

router=APIRouter(tags=["Lakshya"])

@router.post("/khiladi/me/lakshyaBanao",response_model=LakshyaPublic)
async def lakshyabanao(khiladi:Annotated[Khiladi,Depends(get_current_khiladi)],
                       lakshyadata:LakshyaCreate,
                       session:Annotated[Session,Depends(get_session)]):
    db_laskhya=Lakshya.model_validate(lakshyadata,update={"khiladi_id":khiladi.id})
    db_laskhya.khiladi_id=khiladi.id
    session.add(db_laskhya)
    session.commit()
    session.refresh(db_laskhya)
    return db_laskhya


@router.delete("/khiladi/me/{lakshya_id}/deleteLakshya")
async def deletelakshya(khiladi:Annotated[Khiladi,Depends(get_current_khiladi)],lakshya_id:int,session:Annotated[Session,Depends(get_session)]):
   
    statement=select(Lakshya).where((Lakshya.id==lakshya_id)& (Lakshya.khiladi_id==khiladi.id))
    db_lakshya=session.exec(statement).first()
    if not db_lakshya:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, tera ye lakshya exist nhi krta")
    session.delete(db_lakshya)
    session.commit()
    return {"message":f"permananently deleted lakshya with id :{lakshya_id}"}


@router.get("/khiladi/me/lakshyas",response_model=KhiladiWithLakshyas,response_model_exclude_unset=True)
async def get_lakshyas(khiladi:Annotated[Session,Depends(get_current_khiladi)],session:Annotated[Session,Depends(get_session)]):
    return khiladi  

