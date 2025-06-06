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

@router.post("/", response_model=IncomeRead, status_code=status.HTTP_200_OK)
def upsert_income_revised( # Renamed function from previous examples if needed
    income_payload: IncomeCreateBody, # Pydantic validates this first
    session: Session = Depends(get_session)
):
    user = session.get(User, income_payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {income_payload.user_id} not found"
        )

    # Date is validated as a string by Pydantic model, parse it here for DB
    try:
        parsed_date = datetime.strptime(income_payload.date, "%Y-%m-%d").date()
    except ValueError:
        # This case should ideally be caught by the Pydantic validator.
        # If it reaches here, it implies a logic flaw or bypass of Pydantic validation for the format.
        raise HTTPException(status_code=422, detail="Invalid date string passed after Pydantic validation.") # Should not happen
    
    # Amount is validated (non-negative) and Pydantic tries to convert to Decimal.
    # If income_payload.amount is not a valid Decimal after Pydantic's processing,
    # the request would have failed before reaching this point (resulting in 422).
    
    existing_income = session.get(Income, (parsed_date, income_payload.user_id))

    if existing_income:
        existing_income.amount = income_payload.amount # income_payload.amount is already Decimal
        db_income = existing_income
    else:
        # Create new income record using validated and typed data
        db_income = Income(
            user_id=income_payload.user_id,
            date=parsed_date,
            amount=income_payload.amount # income_payload.amount is already Decimal
        )
    
    session.add(db_income)
    session.commit()
    session.refresh(db_income)
    
    # Return using the IncomeRead model to ensure consistent output
    return IncomeRead(user_id=db_income.user_id, date=db_income.date, amount=db_income.amount)