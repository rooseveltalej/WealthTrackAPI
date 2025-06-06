# app/routers/income.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session # Removed select, using session.get
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime # Added datetime

from app.database import get_session
from app.models import Income, User #

# router definition from your previous code block should be here
# router = APIRouter(prefix="/income", tags=["income"])

class IncomeCreateBody(BaseModel):
    user_id: int
    date: str
    amount: Decimal

    @validator('amount')
    def amount_must_be_non_negative(cls, value_from_payload): # Renamed 'value' to avoid clash
        if value_from_payload < 0:
            raise ValueError('Amount cannot be negative')
        return value_from_payload

    @validator('date')
    def date_must_be_valid_format(cls, value_from_payload): # Renamed 'value'
        try:
            datetime.strptime(value_from_payload, "%Y-%m-%d")
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
        return value_from_payload

class IncomeRead(BaseModel): # Keep this for consistent response structure
    user_id: int
    date: pydate
    amount: Decimal

# Ensure the router is defined before use, or use the one from your existing income.py
# If this is a continuation of the income.py file I provided, this router instance is already defined.
# For clarity, I'll re-add the router instance as if it's the start of the relevant section.
router = APIRouter(
    prefix="/income",
    tags=["income"],
)

@router.post("/", response_model=IncomeRead, status_code=status.HTTP_201_CREATED) # Cambiado status code a 201
def create_income( # Renombrado para mayor claridad
    income_payload: IncomeCreateBody,
    session: Session = Depends(get_session)
):
    user = session.get(User, income_payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {income_payload.user_id} not found"
        )

    try:
        # Pydantic ya no valida el formato de fecha, lo hacemos aquí
        parsed_date = datetime.strptime(income_payload.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")

    # La lógica de buscar y actualizar se elimina. Siempre creamos uno nuevo.
    db_income = Income(
        user_id=income_payload.user_id,
        date=parsed_date,
        amount=income_payload.amount
    )
    
    session.add(db_income)
    session.commit()
    session.refresh(db_income)
    
    # Asegúrate de que IncomeRead no espere un id que no tiene
    return IncomeRead(user_id=db_income.user_id, date=db_income.date, amount=db_income.amount)