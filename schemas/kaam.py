from pydantic import BaseModel, Field
from enum import Enum

class difficultylevel(str,Enum):
    easy="easy"
    medium="medium"
    hard="hard"

class Kaam_Create(BaseModel):
    name:str
    description:str|None=None
    xp_reward:int

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
