from enum import Enum
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from schemas.lakshya import Lakshya

# --- ENUMS (State Machines & Categories) ---
class KaamStatus(str, Enum):
    pending = "pending"
    in_review = "in_review"   
    completed = "completed"   
    rejected = "rejected"     

class KaamDifficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    epic = "epic"

# --- MAIN DATABASE TABLE ---
class Kaam(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = Field(default=None)
    xp_reward: int
    deadline: datetime | None = Field(default=None)
    
    
    difficulty: KaamDifficulty = Field(default=KaamDifficulty.medium)
    is_urgent: bool = Field(default=False)
    
    # Core Features
    requires_verification: bool = Field(default=False)
    status: KaamStatus = Field(default=KaamStatus.pending)
    saboot_text: str | None = Field(default=None)        
    saboot_image_url: str | None = Field(default=None)   
    ai_feedback: str | None = Field(default=None)        
    
    # The Relational Locks
    lakshya_id: int = Field(foreign_key="lakshya.id")
    lakshya: "Lakshya" = Relationship(back_populates="kaams")

# --- INPUT: Creating a Task ---
class KaamCreate(SQLModel):
    title: str
    description: str | None = None
    xp_reward: int
    deadline: datetime | None = None
    difficulty: KaamDifficulty = KaamDifficulty.medium
    is_urgent: bool = False
    requires_verification: bool = False 

# --- INPUT: Submitting Proof ---
class KaamSubmit(SQLModel):
    saboot_text: str | None = None
    saboot_image_url: str | None = None

# --- OUTPUT: Safe Return Data ---
class KaamPublic(SQLModel):
    id: int
    title: str
    description: str | None
    xp_reward: int
    deadline: datetime | None
    difficulty: KaamDifficulty
    is_urgent: bool
    requires_verification: bool
    status: KaamStatus
    ai_feedback: str | None


# from pydantic import BaseModel, Field
# from enum import Enum
# from typing import List,TYPE_CHECKING
# from sqlmodel import SQLModel,Field,Relationship
# from datetime import datetime
# if TYPE_CHECKING:
#     from schemas.lakshya import Lakshya


# class Kaam(SQLModel, table=True):
#     id:int|None=Field(default=None,primary_key=True)
#     title:str=Field(index=True)
#     description:str|None=Field(default=None)
#     xp_reward:int
#     deadline:datetime|None=Field(default=None)
#     lakshya_id:int=Field(foreign_key="lakshya.id")
#     lakshya:"Lakshya"=Relationship(back_populates="kaams")
# class Kaam_Create(SQLModel):
#     title:str
#     description:str|None=None
#     xp_reward:int
#     deadline:datetime|None=None

# class KaamUpdate(SQLModel):
#     title:str=Field(min_length=3,max_length=50,description="The new title for the Kaam")
#     new_xp:int=Field(gt=0,le=10000)





