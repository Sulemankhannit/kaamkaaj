from sqlmodel import SQLModel,Field,Relationship,Session,select
from typing import List,TYPE_CHECKING


if TYPE_CHECKING:
    from schemas.kaam import Kaam
    from schemas.khiladi import Khiladi

class LakshyaCreate(SQLModel):
    title:str
    description:str|None=None

class LakshyaPublic(SQLModel):
    id:int
    title:str
    description:str|None=Field(default=None)
    
class Lakshya(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    title:str
    description:str|None=Field(default=None)
    khiladi_id:int=Field(foreign_key="khiladi.id")
    kaams:list["Kaam"]=Relationship(back_populates="lakshya",cascade_delete=True)
    khiladi:"Khiladi"=Relationship(back_populates="lakshyas")