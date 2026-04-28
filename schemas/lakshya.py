from sqlmodel import SQLModel,Field,Relationship
from typing import List,TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.kaam import Kaam

class LakshyaCreate(SQLModel):
    title:str
    description:str|None=None


class Lakshya(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    title:str
    description:str|None=Field(default=None)
    khiladi_id:int=Field(foreign_key="khiladi.id")
    kaams:list["Kaam"]=Relationship(back_populates="lakshya")