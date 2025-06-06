from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date as pydate, datetime
from enum import Enum
from typing import Optional

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
    date: pydate
    amount: Decimal
    category: SavingCategory

# Modelo para la actualización, con campos opcionales
class SavingUpdate(BaseModel):
    date: Optional[pydate] = None
    amount: Optional[Decimal] = None
    category: Optional[SavingCategory] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

router = APIRouter(prefix="/saving", tags=["saving"])

@router.post("/", response_model=Saving, status_code=status.HTTP_201_CREATED)
def create_saving(saving_in: SavingCreate, session: Session = Depends(get_session)):
    user = session.get(User, saving_in.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_saving = Saving.from_orm(saving_in)
    session.add(db_saving)
    session.commit()
    session.refresh(db_saving)
    return db_saving

@router.put("/{saving_id}", response_model=Saving)
def update_saving(saving_id: int, saving_in: SavingUpdate, session: Session = Depends(get_session)):
    db_saving = session.get(Saving, saving_id)
    if not db_saving:
        raise HTTPException(status_code=404, detail="Saving not found")
    
    saving_data = saving_in.dict(exclude_unset=True)
    for key, value in saving_data.items():
        setattr(db_saving, key, value)

    session.add(db_saving)
    session.commit()
    session.refresh(db_saving)
    return db_saving

@router.delete("/{saving_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saving(saving_id: int, session: Session = Depends(get_session)):
    db_saving = session.get(Saving, saving_id)
    if not db_saving:
        raise HTTPException(status_code=404, detail="Saving not found")
    
    session.delete(db_saving)
    session.commit()
    return