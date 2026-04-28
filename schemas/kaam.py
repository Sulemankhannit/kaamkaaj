from pydantic import BaseModel, Field
from enum import Enum
from typing import List,TYPE_CHECKING
from sqlmodel import SQLModel,Field,Relationship
from datetime import datetime
if TYPE_CHECKING:
    from schemas.lakshya import Lakshya


class Kaam(SQLModel, table=True):
    id:int|None=Field(default=None,primary_key=True)
    title:str=Field(index=True)
    description:str|None=Field(default=None)
    xp_reward:int
    deadline:datetime|None=Field(default=None)
    lakshya_id:int=Field(foreign_key="lakshya.id")
    lakshya:"Lakshya"=Relationship(back_populates="kaams")


class difficultylevel(str,Enum):
    easy="easy"
    medium="medium"
    hard="hard"

class Kaam_Create(BaseModel):
    name:str
    description:str|None=None
    xp_reward:int
    deadline:datetime|None=None

class KaamUpdate(BaseModel):
    title:str=Field(min_length=3,max_length=50,description="The new title for the Kaam")
    new_xp:int=Field(gt=0,le=10000)


class KaamResolution(BaseModel):
    status:str
    hours_spent:int

class Saboot(BaseModel):
    file_url:str
    description:str


class KaamLocation(BaseModel):
    city:str
    danger_level:str

class KammDetailedCreate(BaseModel):
    title:str
    description:str|None=None
    tags:set[str]
    location:KaamLocation
