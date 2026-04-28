from sqlmodel import SQLModel,Field

class Khiladi(SQLModel,table=True):
    id:int|None=Field(primary_key=True,default=None)
    username:str=Field(unique=True,index=True)
    password:str
    email:str
    level:int=Field(default=1)
    clan_name:str|None=Field(default=None)
    bio:str|None=Field(default=None)
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

