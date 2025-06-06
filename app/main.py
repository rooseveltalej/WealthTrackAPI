# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select

from app.database import engine, get_session
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.dashboard import router as dashboard_router
from app.routers.goals import router as goals_router
from app.routers.income import router as income_router # New Import
from app.routers import history
from app.routers import profile


app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://localhost:5173",
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
app.include_router(users_router)
app.include_router(dashboard_router)
app.include_router(history.router)
app.include_router(goals_router)
app.include_router(profile.router)
app.include_router(income_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
