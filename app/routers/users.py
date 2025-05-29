# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from app.database import get_session
from app.models import User, UserRead, UserCreate

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_in: UserCreate,
    session: Session = Depends(get_session)
):
    # Check if the email already exists
    existing = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    
    user = User(**user_in.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def read_user(
    user_id: int,
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
