from sqlmodel import SQLModel,Field,Relationship
from typing import List,TYPE_CHECKING
from datetime import datetime,date
from pydantic import BaseModel,EmailStr
from schemas.lakshya import LakshyaPublic
if TYPE_CHECKING:
    from schemas.lakshya import Lakshya

class Khiladi(SQLModel,table=True):
    id:int|None=Field(primary_key=True,default=None)
    username:str=Field(unique=True,index=True)
    hashed_password:str
    email:str=Field(unique=True,index=True)
    level:int=Field(default=1)
    total_xp:int=Field(default=0)
    xp_debt:int=Field(default=0)
    clan_name:str|None=Field(default=None)
    bio:str|None=Field(default=None)
    is_verified: bool = Field(default=False)
    otp_code: str | None = Field(default=None)
    otp_expires_at: datetime | None = Field(default=None)
    lakshyas:list["Lakshya"]=Relationship(back_populates="khiladi",cascade_delete=True)
    pro_user:bool=Field(default=False)
    current_streak:int=Field(default=0)
    longest_streak:int=Field(default=0)
    last_streak_date:date|None=Field(default=None)
    streak_freezes:int=Field(default=0)

class KhiladiCreate(SQLModel):
    username:str
    email:str
    password:str

class KhiladiPublic(SQLModel):
    id:int
    username:str
    email:str
    level:int
    total_xp:int
    xp_debt:int = 0
    clan_name:str|None=None
    bio:str|None=None
    current_streak:int=0
    longest_streak:int=0
    last_streak_date:date|None=None
    streak_freezes:int=0

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
class DeleteProfile(BaseModel):
    password:str

class KhiladiWithLakshyas(KhiladiProfile):
    lakshyas:list[LakshyaPublic]=[]

class VerifyOtp(BaseModel):
    email:str
    user_otp:str
class ResendOtpRequest(BaseModel):
    email: EmailStr

