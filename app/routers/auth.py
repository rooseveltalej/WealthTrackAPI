# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import BaseModel

from app.database import get_session
from app.models import User, UserRead

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login", response_model=UserRead)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    stmt = select(User).where(User.email == request.email)
    user = session.exec(stmt).first()

    if not user or user.password != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    return user
