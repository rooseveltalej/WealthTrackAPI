import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlmodel import Session, select
from sqlalchemy import extract

from app.database import get_session
from app.models import (
    User, Income, Expense, Saving, Investment,
    ExpenseGoal, SavingGoal, InvestmentGoal
)

router = APIRouter(
    prefix="/import",
    tags=["import"],
)

# Función auxiliar para 'upsert' de metas
def _upsert_goal(session: Session, Model, user_id: int, date: datetime.date, value: Decimal):
    year = date.year
    month = date.month
    
    existing = session.exec(
        select(Model)
        .where(
            Model.user_id == user_id,
            extract("year", Model.date) == year,
            extract("month", Model.date) == month
        )
    ).first()

    if existing:
        existing.value = value
        session.add(existing)
    else:
        goal = Model(user_id=user_id, date=date, value=value)
        session.add(goal)

# Función auxiliar para 'upsert' de ingresos
def _upsert_income(session: Session, user_id: int, date: datetime.date, amount: Decimal):
    # En el modelo actual, Income no tiene ID y la PK es (date, user_id).
    # Para la regla "un único valor por mes", primero borramos los existentes para ese mes.
    year = date.year
    month = date.month
    
    stmt_delete = (
        Income.__table__.delete()
        .where(Income.user_id == user_id)
        .where(extract("year", Income.date) == year)
        .where(extract("month", Income.date) == month)
    )
    session.exec(stmt_delete)
    
    # Insertamos el nuevo
    new_income = Income(user_id=user_id, date=date, amount=amount)
    session.add(new_income)


@router.post("/csv")
async def import_csv_data(
    *,
    email: str = Form(...),
    data_type: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content = await file.read()
    try:
        decoded_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please use UTF-8.")

    csv_reader = csv.reader(io.StringIO(decoded_content))
    
    # Omitir el encabezado
    try:
        next(csv_reader)
    except StopIteration:
        raise HTTPException(status_code=400, detail="CSV file is empty.")

    records_to_add = []
    
    try:
        if data_type in ["expenses", "savings", "investments"]:
            Model = {"expenses": Expense, "savings": Saving, "investments": Investment}[data_type]
            for i, row in enumerate(csv_reader, 2):
                if len(row) != 3:
                    raise HTTPException(400, f"Row {i}: Expected 3 columns, found {len(row)}")
                date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
                amount_val = Decimal(row[1])
                records_to_add.append(Model(user_id=user.id, date=date_obj, amount=amount_val, category=row[2]))
            session.add_all(records_to_add)

        elif data_type in ["expense_goals", "saving_goals", "investment_goals"]:
            Model = {"expense_goals": ExpenseGoal, "saving_goals": SavingGoal, "investment_goals": InvestmentGoal}[data_type]
            for i, row in enumerate(csv_reader, 2):
                if len(row) != 2:
                    raise HTTPException(400, f"Row {i}: Expected 2 columns, found {len(row)}")
                date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
                value_val = Decimal(row[1])
                _upsert_goal(session, Model, user.id, date_obj, value_val)
        
        elif data_type == "income":
            for i, row in enumerate(csv_reader, 2):
                if len(row) != 2:
                    raise HTTPException(400, f"Row {i}: Expected 2 columns, found {len(row)}")
                date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
                amount_val = Decimal(row[1])
                _upsert_income(session, user.id, date_obj, amount_val)

        else:
            raise HTTPException(status_code=400, detail=f"Invalid data type: {data_type}")
        
        session.commit()

    except (ValueError, InvalidOperation) as e:
        raise HTTPException(status_code=422, detail=f"Data format error in CSV: {e}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    return {"message": f"{data_type.replace('_', ' ').capitalize()} imported successfully"}