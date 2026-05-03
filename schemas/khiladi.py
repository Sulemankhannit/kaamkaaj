from sqlmodel import SQLModel,Field,Relationship
from typing import List,TYPE_CHECKING
from schemas.lakshya import LakshyaPublic
if TYPE_CHECKING:
    from schemas.lakshya import Lakshya

class Khiladi(SQLModel,table=True):
    id:int|None=Field(primary_key=True,default=None)
    username:str=Field(unique=True,index=True)
    hashed_password:str
    email:str
    level:int=Field(default=1)
    total_xp:int=Field(default=0)
    clan_name:str|None=Field(default=None)
    bio:str|None=Field(default=None)
    lakshyas:list["Lakshya"]=Relationship(back_populates="khiladi")
    pro_user:bool=Field(default=False)

class KhiladiCreate(SQLModel):
    username:str
    email:str
    password:str

class KhiladiPublic(SQLModel):
    id:int
    username:str
    email:str
    level:int

class KhiladiProfile(SQLModel):
    username:str
    level:int=1
    clan_name:str|None=None
    bio:str|None=None

class KhiladiUpdate(SQLModel):
    password:str|None=None
    email:str|None=None
    clan_name:str|None=None
    bio:str|None=None


class KhiladiWithLakshyas(KhiladiProfile):
    lakshyas:list[LakshyaPublic]=[]

