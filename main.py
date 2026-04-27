from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes import khiladi,kaam
from sqlmodel import SQLModel
from core.config import engine
from schemas.khiladi import Khiladi
app=FastAPI()
@app.on_event("startup")
def on_startup():
    print("compiling database tables")
    SQLModel.metadata.create_all(engine)


@app.exception_handler(RequestValidationError)
async def validation_exceptio_handler(request,exc:RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "Bhai, the data you sent is invalid! Check your fields.",
            "technical_details": exc.errors() 
        }
    )

app.include_router(khiladi.router)
app.include_router(kaam.router)
@app.get("/")
async def welcome_to_kaamkaj():
    return{
       "message":"Welcome to tavern,Adventurer",
       "status":"server is correctly runnning."
    }

@app.get("/artifacts/{filepath:path}")
async def getfile(filepath:str):
    print("seraching for {filepath} in server")
    return {
        "message":f"found your {filepath}",
        "download url":f"https://questlog/{filepath}"
    }









   


