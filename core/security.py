import bcrypt
import jwt
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordBearer
from schemas.khiladi import Khiladi
from fastapi import HTTPException,Depends,status
from sqlmodel import Session,select
from core.config import get_session
from jwt.exceptions import InvalidTokenError

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

# In production, NEVER hardcode this. It should be in your .env file!
SECRET_KEY = "KaamKaaj_Super_Secret_Key_For_Suleman_Only_Do_Not_Share"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60*24*7 #7 days expiry

def get_hashed_password(password:str)->str:
    salt=bcrypt.gensalt()
    hashed_password=bcrypt.hashpw(password.encode("utf-8"),salt)
    return hashed_password.decode("utf-8")

def check_password(plain_password:str,hashed_password:str)->bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"),hashed_password.encode("utf-8"))



def create_access_token(data:dict)->str:
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

def get_current_khiladi(
    # 1. FastAPI intercepts the packet and grabs the token string using the scheme we built
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> Khiladi:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 2. Mathematically verify the signature and check the expiration time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 3. Extract the username we stored in the "sub" field during login
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except InvalidTokenError:
        # If the math fails, or the token is expired, kick them out immediately.
        raise credentials_exception

    # 4. Fetch the Khiladi from PostgreSQL using the verified username
    statement = select(Khiladi).where(Khiladi.username == username)
    khiladi = session.exec(statement).first()
    
    if khiladi is None:
        raise credentials_exception
        
    # 5. Hand the full database object over to your route!
    return khiladi