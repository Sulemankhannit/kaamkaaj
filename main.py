from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from routes import khiladi,kaam,lakshya,auth,dashboard
from sqlmodel import SQLModel
from core.config import engine
from schemas.khiladi import Khiladi
from schemas.kaam import Kaam
from schemas.lakshya import Lakshya
from schemas.daily_message import DailyMessage
from core.limiter import Limiter,limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from utils.reaper import run_reaper
import asyncio
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class VercelLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # If it's a success (200-299)
            if 200 <= response.status_code < 300:
                print(f"✅ VERCEL LOG: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
            
            # If it's a soft error (400-499 like bad validation or unauthorized)
            elif 400 <= response.status_code < 500:
                print(f"⚠️ VERCEL WARNING: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
                
            # If it's a server crash (500+)
            else:
                print(f"❌ VERCEL ERROR: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
                
            return response

        except Exception as e:
            # If a catastrophic error bypasses FastAPI's error handler
            process_time = time.time() - start_time
            print(f"🔥 VERCEL FATAL CRASH: {request.method} {request.url.path} - Exception: {str(e)} - Time: {process_time:.4f}s")
            raise e
reaper_task = None

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global reaper_task
#     reaper_task = asyncio.create_task(run_reaper())
#     yield
#     if reaper_task:
#         reaper_task.cancel()
#         try:
#             await reaper_task
#         except asyncio.CancelledError:
#             pass

app=FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"], # Allow your Next.js frontend
#     allow_credentials=True,
#     allow_methods=["*"], # Allow all types of requests (GET, POST, PATCH, etc.)
#     allow_headers=["*"], # Allow all headers (like Authorization for your JWTs)
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", # Allows  local frontend during testing
        "https://kaamkaaj-sooty.vercel.app" # Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, PUT, DELETE
    allow_headers=["*"],
)
app.add_middleware(VercelLoggingMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
app.include_router(lakshya.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
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









   


