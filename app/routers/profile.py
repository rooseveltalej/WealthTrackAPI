from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, select, Session
from sqlalchemy import desc

from app.database import get_session
from app.models import User, ExpenseGoal, SavingGoal, InvestmentGoal

router = APIRouter(prefix="/profile", tags=["profile"])


class GoalInfo(SQLModel):
    date: date
    value: Decimal


class ProfileResponse(SQLModel):
    id: int
    email: str
    username: Optional[str] = None

    expense_goal:     Optional[GoalInfo] = None
    saving_goal:      Optional[GoalInfo] = None
    investment_goal:  Optional[GoalInfo] = None


@router.get("/{user_id}", response_model=ProfileResponse)
def read_profile(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    if today.month == 12:
        first_of_next = date(today.year + 1, 1, 1)
    else:
        first_of_next = date(today.year, today.month + 1, 1)

    def get_goal_for_month_or_last(
        GoalModel,
    ) -> Optional[GoalInfo]:

        stmt_current = (
            select(GoalModel)
            .where(
                (GoalModel.user_id == user_id),
                (GoalModel.date >= first_of_month),
                (GoalModel.date < first_of_next),
            )
            .order_by(desc(GoalModel.date))  # Traer la más reciente de este mes
        )
        current = session.exec(stmt_current).first()
        if current:
            return GoalInfo(date=current.date, value=current.value)

        stmt_last = (
            select(GoalModel)
            .where(GoalModel.user_id == user_id)
            .order_by(desc(GoalModel.date))
        )
        last = session.exec(stmt_last).first()
        if last:
            return GoalInfo(date=last.date, value=last.value)

        return None


    expense_goal = get_goal_for_month_or_last(ExpenseGoal)
    saving_goal = get_goal_for_month_or_last(SavingGoal)
    investment_goal = get_goal_for_month_or_last(InvestmentGoal)

    resolved_username = user.username or user.email
    return ProfileResponse(
        id=user.id,
        email=user.email,
        username=resolved_username,
        expense_goal=expense_goal,
        saving_goal=saving_goal,
        investment_goal=investment_goal,
    )

class ProfileUpdateRequest(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


@router.put("/{user_id}", response_model=ProfileResponse)
def update_profile(
    user_id: int,
    payload: ProfileUpdateRequest,
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    if payload.email and payload.email != user.email:
        exists = session.exec(select(User).where(User.email == payload.email)).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro usuario con ese correo."
            )
        user.email = payload.email.strip()

    if payload.username is not None:
        user.username = payload.username.strip()

    if payload.password:
        user.password = payload.password

    session.add(user)
    session.commit()
    session.refresh(user)

    resolved_username = user.username or user.email
    return ProfileResponse(
        id=user.id,
        email=user.email,
        username=resolved_username
    )