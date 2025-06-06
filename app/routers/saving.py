from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime
from enum import Enum

from app.database import get_session
from app.models import Saving, User

class SavingCategory(str, Enum):
    fondo_de_emergencia = "fondo de emergencia"
    jubilacion = "jubilación"
    vacaciones = "vacaciones"
    mantenimiento = "mantenimiento"
    otros = "otros"

class SavingCreate(BaseModel):
    user_id: int
    date: str # Se espera una cadena de texto, no un objeto de fecha
    amount: Decimal
    category: SavingCategory

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v


router = APIRouter(prefix="/saving", tags=["saving"])

@router.post("/", response_model=Saving, status_code=status.HTTP_201_CREATED)
def create_saving(saving_in: SavingCreate, session: Session = Depends(get_session)):
    user = session.get(User, saving_in.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_saving = Saving.from_orm(saving_in)

    try:
        parsed_date = datetime.strptime(saving_in.date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")

    # Creamos el objeto para la BD con la fecha ya procesada
    db_saving = Saving(
        user_id=saving_in.user_id,
        date=parsed_date,
        amount=saving_in.amount,
        category=saving_in.category
    )

    session.add(db_saving)
    session.commit()
    session.refresh(db_saving)
    return db_saving