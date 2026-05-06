from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from core.security import get_current_khiladi,get_session
from schemas.khiladi import Khiladi
from schemas.lakshya import Lakshya
from schemas.dashboard import DashboardKaamResponse,DashboardLakshyaResponse,DashboardResponse
router=APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_khiladi_dashboard(
    current_khiladi: Khiladi = Depends(get_current_khiladi),
    session: Session = Depends(get_session)
):
   
    statement = (
        select(Khiladi)
        .where(Khiladi.id == current_khiladi.id)
        .options(
            selectinload(Khiladi.lakshyas).selectinload(Lakshya.kaams)
        )
    )
    db_khiladi = session.exec(statement).first()

   
    
    lakshyas_list = []
    
    # Loop through the eagerly loaded Lakshyas
    for lak in db_khiladi.lakshyas:
        
        kaams_list = []
       
        for kaam in lak.kaams:
            kaams_list.append(
                DashboardKaamResponse(
                    id=kaam.id,
                    title=kaam.title,
                    description=kaam.description,
                    status=kaam.status,
                    xp_reward=kaam.xp_reward,
                    requires_verification=kaam.requires_verification,
                    deadline=kaam.deadline
                )
            )
            
       
        lakshyas_list.append(
            DashboardLakshyaResponse(
                id=lak.id,
                title=lak.title,
                description=lak.description,
                is_accomplished=lak.is_accomplished,
                deadline=lak.deadline,
                kaams=kaams_list
            )
        )

    
    dashboard = DashboardResponse(
        khiladi_id=db_khiladi.id,
        name=db_khiladi.username,
        level=db_khiladi.level,
        current_xp=db_khiladi.total_xp, # Make sure this exactly matches your DB Khiladi column name! (e.g., xp or current_xp)
        lakshyas=lakshyas_list
    )

    # 3. SHIP IT
    return dashboard
