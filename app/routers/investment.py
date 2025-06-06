from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime
from enum import Enum
from typing import Optional

from app.database import get_session
from app.models import Investment, User

class InvestmentCategory(str, Enum):
    fondo_de_inversion = "fondo de inversión"
    acciones = "acciones"
    bienes_raices = "bienes raíces"
    cripto = "cripto"
    negocio = "negocio"
    otros = "otros"

class InvestmentCreate(BaseModel):
    user_id: int
    date: pydate
    amount: Decimal
    category: InvestmentCategory

# Modelo para la actualización
class InvestmentUpdate(BaseModel):
    date: Optional[pydate] = None
    amount: Optional[Decimal] = None
    category: Optional[InvestmentCategory] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

router = APIRouter(prefix="/investment", tags=["investment"])

@router.post("/", response_model=Investment, status_code=status.HTTP_201_CREATED)
def create_investment(investment_in: InvestmentCreate, session: Session = Depends(get_session)):
    user = session.get(User, investment_in.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_investment = Investment.from_orm(investment_in)
    session.add(db_investment)
    session.commit()
    session.refresh(db_investment)
    return db_investment

@router.put("/{investment_id}", response_model=Investment)
def update_investment(investment_id: int, investment_in: InvestmentUpdate, session: Session = Depends(get_session)):
    db_investment = session.get(Investment, investment_id)
    if not db_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    investment_data = investment_in.dict(exclude_unset=True)
    for key, value in investment_data.items():
        setattr(db_investment, key, value)

    session.add(db_investment)
    session.commit()
    session.refresh(db_investment)
    return db_investment

@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(investment_id: int, session: Session = Depends(get_session)):
    db_investment = session.get(Investment, investment_id)
    if not db_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    session.delete(db_investment)
    session.commit()
    return