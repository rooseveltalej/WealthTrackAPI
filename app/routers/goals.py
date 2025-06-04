from fastapi import APIRouter, Depends, status
from sqlmodel import select, Session
from sqlalchemy import extract
from datetime import datetime

from app.database import get_session
from app.models import ExpenseGoal, SavingGoal, InvestmentGoal

router = APIRouter(prefix="/goals", tags=["goals"])

def upsert_goal(session: Session, Model, goal_in):
    # Convertir str a date si es necesario
    if isinstance(goal_in.date, str):
        goal_in.date = datetime.strptime(goal_in.date, "%Y-%m-%d").date()

    year = goal_in.date.year
    month = goal_in.date.month

    existing = session.exec(
        select(Model)
        .where(
            Model.user_id == goal_in.user_id,
            extract("year", Model.date) == year,
            extract("month", Model.date) == month
        )
    ).first()

    if existing:
        existing.date = goal_in.date
        existing.value = goal_in.value
        goal = existing
    else:
        goal = Model(**goal_in.dict())

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal



@router.post("/expense", response_model=ExpenseGoal, status_code=status.HTTP_200_OK)
def upsert_expense_goal(goal_in: ExpenseGoal, session: Session = Depends(get_session)):
    return upsert_goal(session, ExpenseGoal, goal_in)


@router.post("/saving", response_model=SavingGoal, status_code=status.HTTP_200_OK)
def upsert_saving_goal(goal_in: SavingGoal, session: Session = Depends(get_session)):
    return upsert_goal(session, SavingGoal, goal_in)


@router.post("/investment", response_model=InvestmentGoal, status_code=status.HTTP_200_OK)
def upsert_investment_goal(goal_in: InvestmentGoal, session: Session = Depends(get_session)):
    return upsert_goal(session, InvestmentGoal, goal_in)