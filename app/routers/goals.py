# app/routers/goals.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from app.database import get_session
from app.models import ExpenseGoal, SavingGoal, InvestmentGoal

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post(
    "/expense",
    response_model=ExpenseGoal,
    status_code=status.HTTP_201_CREATED
)
def create_expense_goal(
    goal_in: ExpenseGoal,
    session: Session = Depends(get_session)
):
    existing = session.exec(
        select(ExpenseGoal)
        .where(
            (ExpenseGoal.date == goal_in.date) &
            (ExpenseGoal.user_id == goal_in.user_id)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una meta de gasto para esta fecha y usuario."
        )

    session.add(goal_in)
    session.commit()
    session.refresh(goal_in)
    return goal_in


@router.post(
    "/saving",
    response_model=SavingGoal,
    status_code=status.HTTP_201_CREATED
)
def create_saving_goal(
    goal_in: SavingGoal,
    session: Session = Depends(get_session)
):
    existing = session.exec(
        select(SavingGoal)
        .where(
            (SavingGoal.date == goal_in.date) &
            (SavingGoal.user_id == goal_in.user_id)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una meta de ahorro para esta fecha y usuario."
        )

    session.add(goal_in)
    session.commit()
    session.refresh(goal_in)
    return goal_in


@router.post(
    "/investment",
    response_model=InvestmentGoal,
    status_code=status.HTTP_201_CREATED
)
def create_investment_goal(
    goal_in: InvestmentGoal,
    session: Session = Depends(get_session)
):
    existing = session.exec(
        select(InvestmentGoal)
        .where(
            (InvestmentGoal.date == goal_in.date) &
            (InvestmentGoal.user_id == goal_in.user_id)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una meta de inversión para esta fecha y usuario."
        )

    session.add(goal_in)
    session.commit()
    session.refresh(goal_in)
    return goal_in