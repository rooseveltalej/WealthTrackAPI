from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime
from enum import Enum
from typing import Optional

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

class ExpenseUpdate(BaseModel):
    date: Optional[pydate] = None
    amount: Optional[Decimal] = None
    category: Optional[ExpenseCategory] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        if v and isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")
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


@router.put("/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, expense_in: ExpenseUpdate, session: Session = Depends(get_session)):
    db_expense = session.get(Expense, expense_id)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # El modelo Pydantic ya maneja la conversión de la fecha, por lo que el bucle se simplifica.
    expense_data = expense_in.dict(exclude_unset=True)
    for key, value in expense_data.items():
        setattr(db_expense, key, value)

    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    db_expense = session.get(Expense, expense_id)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    session.delete(db_expense)
    session.commit()
    return