# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.database import engine
from app.routers.auth import router as auth_router

app = FastAPI()

origins = [
    "http://localhost:8080", 
    "http://localhost:5173", # maes ignoren esto es que todavía no lo he pasado a apache 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLModel.metadata.create_all(engine)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}