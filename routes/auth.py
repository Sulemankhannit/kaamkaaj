from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated

from core.config import get_session
from schemas.khiladi import Khiladi
from core.security import check_password,create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/login")
async def login_for_access_token(
    # This dependency forces the client to send application/x-www-form-urlencoded data
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    # 1. Find the Khiladi in the database
    statement = select(Khiladi).where(Khiladi.username == form_data.username)
    db_khiladi = session.exec(statement).first()

    # 2. Verify existence AND password match
    if not db_khiladi or not check_password(form_data.password, db_khiladi.hashed_password):
        # We give a generic error.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not db_khiladi.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bhai, pehle apna email verify kar! Use /resendOtp if you need a new code.")
    
    jwt_payload = {"sub": db_khiladi.username, "khiladi_id": db_khiladi.id}
    token = create_access_token(data=jwt_payload)

   
    return {
        "access_token": token, 
        "token_type": "bearer"
    }
