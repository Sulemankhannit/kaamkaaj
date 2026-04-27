from fastapi import Query,Path,status,HTTPException,Body,APIRouter,Depends
from typing import Annotated
from schemas.kaam import Kaam_Create,KaamLocation,KaamResolution,KaamUpdate,KammDetailedCreate,difficultylevel,Saboot



router=APIRouter(
    prefix="/kaam",
    tags=["Kaam"]
    )
class  KaamPaginationParams:
     def __init__(self,skip:int=0,limit:int=10):
         self.skip=skip
         self.limit=limit


def extract_search_query(q: str | None = None):
    if q:
        return q.lower()
    return None

def get_advanced_filters(
    pagination: Annotated[KaamPaginationParams, Depends()],
    search_keyword: Annotated[str | None, Depends(extract_search_query)]
):
    return {
        "skip": pagination.skip,
        "limit": pagination.limit,
        "search": search_keyword
    }

@router.get("/difficulty/{level}")
async def get_difficulty_wise_kaam(level:difficultylevel):
    if level==difficultylevel.hard:
        return {"message":"most dangerous quest"}
    elif level==difficultylevel.medium:
        return {"message":"medium quest"}
    else:
        return {"message":"cake walk quest"}
    
@router.get("/search")
async def searchKaam(query:Annotated[str|None, Query(min_length=3,max_length=20,pattern="^[a-zA-Z0-9 ]+$")]=None):
    if query is None:
        return {"message":"Please provide kaam name for the search "}
    else:
        return {"message":f"searching for {query} !"}
    

@router.get("/filter/tags")
async def filterkaam(tags:Annotated[list[str]|None,Query(alias="kaam-tags",title="Kaam Tags",description="Filter your Kaam by multiple categories (e.g., study, workout).")]=None):
    if not tags:
        return {"message":"provide tags for filtering"}
    else:
        return {"message":f"filtering kaam with respect to {tags}"}



@router.get("/{kaam_id}")
async def get_kaam(kaam_id:Annotated[int,Path(ge=1,le=1000)],xp_multiply:Annotated[float,Query(ge=0,le=5.0)]=None):
    if xp_multiply is None:
        message="None"
    else:
        message=xp_multiply
    if kaam_id>100:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai, yeh kaam exist nahi karta")
    return {
        "kaam_id": kaam_id,
        "kaam_name": f"Defeat the Goblin King (ID: {kaam_id})",
        "xp_reward_muliplier": message,
        "status": "Incomplete"
    }


@router.get("/")
async def list_kaams(filters:Annotated[dict,Depends(get_advanced_filters)]):
    return {
        "message":f"Fetching quests from the database...",
        "filters_applied":filters
    }

@router.post("/")
async def create_kaam(kaam:Kaam_Create):
    print("Server log:quest is being created")
    return{
        "message":f"your quest named:{kaam.name} and worth {kaam.xp_reward}xp is created!",
        "quest_data":kaam
    }
    

@router.put("/{kaam_id}")
async def updatekaam(kaam_id:int,kaam_data:KaamUpdate,notify_khiladi:bool=False):
    return{
        "message":"Successfully updated",
        "updated_id":kaam_id,
        "updated kaam":kaam_data,
        "notify_khildai":notify_khiladi
    }

@router.put("/{kaam_id}/submit")
async def submit_kaam(
    kaam_id:int,
    resolution:KaamResolution,
    proof:Saboot,
    rating:Annotated[int,Body(ge=1,le=5)]=None
    ):
    return {
        "message":"Kaam submitted successfully",
        "submitted_kaam_id":kaam_id,
        "resolution":resolution,
        "Saboot":proof
    }

@router.post("/Advanced/create")
async def createDetailedKaam(
    deatiledkaamdata:KammDetailedCreate
):
 return {"message":"detailed kaam created",
        "kaam_data":deatiledkaamdata}

