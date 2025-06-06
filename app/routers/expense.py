from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime
from enum import Enum

from app.database import get_session
from app.models import Expense, User

class ExpenseCategory(str, Enum):
    vivienda = "vivienda"
    alimentacion = "alimentación"
    transporte = "transporte"
    salud = "salud"
    educacion = "educación"
    entretenimiento = "entretenimiento"
    ropa = "ropa"
    otros = "otros"

class ExpenseCreate(BaseModel):
    user_id: int
    date: pydate
    amount: Decimal
    category: ExpenseCategory

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

router = APIRouter(prefix="/expense", tags=["expense"])

@router.post("/", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(expense_in: ExpenseCreate, session: Session = Depends(get_session)):
    user = session.get(User, expense_in.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_expense = Expense.from_orm(expense_in)
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense