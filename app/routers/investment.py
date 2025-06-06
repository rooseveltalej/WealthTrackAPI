from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime
from enum import Enum

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
    date: str # Se espera una cadena de texto
    amount: Decimal
    category: InvestmentCategory

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v


router = APIRouter(prefix="/investment", tags=["investment"])

@router.post("/", response_model=Investment, status_code=status.HTTP_201_CREATED)
def create_investment(investment_in: InvestmentCreate, session: Session = Depends(get_session)):
    user = session.get(User, investment_in.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        parsed_date = datetime.strptime(investment_in.date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")

    # Creamos el objeto para la BD con la fecha ya procesada
    db_investment = Investment(
        user_id=investment_in.user_id,
        date=parsed_date,
        amount=investment_in.amount,
        category=investment_in.category
    )


    session.add(db_investment)
    session.commit()
    session.refresh(db_investment)
    return db_investment