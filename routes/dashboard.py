from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from core.security import get_current_khiladi,get_session
from schemas.khiladi import Khiladi
from schemas.lakshya import Lakshya
from schemas.dashboard import DashboardKaamResponse,DashboardLakshyaResponse,DashboardResponse
router=APIRouter(tags=["Dashboard"])

XP_PER_LEVEL = 1000

def get_shadow_realm_status(total_xp: int) -> tuple[bool, str | None]:
    """Check if user is in the Shadow Realm (negative XP)."""
    if total_xp < 0:
        return True, f"You have fallen into the Shadow Realm with {abs(total_xp)} XP in debt. Complete tasks to escape!"
    return False, None

def get_xp_progress(total_xp: int) -> tuple[int, int]:
    """Get XP progress within current level and XP needed for next level."""
    if total_xp < 0:
        return 0, XP_PER_LEVEL
    current_level_xp = total_xp % XP_PER_LEVEL
    xp_needed = XP_PER_LEVEL - current_level_xp
    return current_level_xp, xp_needed

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

    in_shadow_realm, shadow_message = get_shadow_realm_status(db_khiladi.total_xp)
    net_xp = db_khiladi.total_xp - db_khiladi.xp_debt
    current_progress, xp_to_next = get_xp_progress(db_khiladi.total_xp)
    
    lakshyas_list = []
    
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
        current_xp=db_khiladi.total_xp,
        xp_debt=db_khiladi.xp_debt,
        in_shadow_realm=in_shadow_realm,
        shadow_realm_message=shadow_message,
        net_xp=net_xp,
        xp_to_next_level=xp_to_next,
        lakshyas=lakshyas_list
    )

    return dashboard
