from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from core.security import get_current_khiladi,get_session
from schemas.khiladi import Khiladi
from schemas.lakshya import Lakshya
from schemas.dashboard import DashboardKaamResponse,DashboardLakshyaResponse,DashboardResponse
router=APIRouter(tags=["Dashboard"])
# (Assuming you imported Khiladi, Lakshya, Kaam, get_session, get_current_khiladi)
# (Assuming you imported your new Dashboard schemas)

@router.get("/dashboard", response_model=DashboardResponse)
async def get_khiladi_dashboard(
    current_khiladi: Khiladi = Depends(get_current_khiladi),
    session: Session = Depends(get_session)
):
    # ==========================================
    # 1. THE ENGINE (The N+1 Killer)
    # ==========================================
    statement = (
        select(Khiladi)
        .where(Khiladi.id == current_khiladi.id)
        .options(
            selectinload(Khiladi.lakshyas).selectinload(Lakshya.kaams)
        )
    )
    db_khiladi = session.exec(statement).first()

    # ==========================================
    # 2. THE ASSEMBLY (Russian Nesting Dolls)
    # ==========================================
    
    lakshyas_list = []
    
    # Loop through the eagerly loaded Lakshyas
    for lak in db_khiladi.lakshyas:
        
        kaams_list = []
        # Loop through the eagerly loaded Kaams inside this specific Lakshya
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
            
        # Assemble the Lakshya and attach the list of Kaams
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

    # Assemble the final Top-Level Dashboard
    dashboard = DashboardResponse(
        khiladi_id=db_khiladi.id,
        name=db_khiladi.username,
        level=db_khiladi.level,
        current_xp=db_khiladi.total_xp, # Make sure this exactly matches your DB Khiladi column name! (e.g., xp or current_xp)
        lakshyas=lakshyas_list
    )

    # 3. SHIP IT
    return dashboard