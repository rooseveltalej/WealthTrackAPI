from datetime import date as pydate
from dateutil.relativedelta import relativedelta
from typing import List, Literal, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, extract
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    User,
    Income,
    Expense,
    Saving,
    Investment,
    ExpenseGoal,
    SavingGoal,
    InvestmentGoal,
)

router = APIRouter(
    prefix="/history",
    tags=["history"],
)


# ─── Modelos de respuesta ────────────────────────────────────────────────────────

class SimpleHistoryEntry(BaseModel):
    year: int
    month: int
    total: float


class SimpleHistoryResponse(BaseModel):
    entries: List[SimpleHistoryEntry]
    total_sum: float
    average: float


class GoalHistoryEntry(BaseModel):
    year: int
    month: int
    goal_value: float
    actual_value: float
    met: bool

class GoalHistoryResponse(BaseModel):
    entries: List[GoalHistoryEntry]
    total_goal_value: float
    average_goal_value: float
    goal_met_percentage: float

# ─── Función auxiliar para calcular fecha de inicio ───────────────────────────────

def _compute_start_date(period_months):
    period_months = int(period_months)
    today = pydate.today()
    start = today - relativedelta(months=period_months)
    return pydate(year=start.year, month=start.month, day=1)


# ─── Ruta GET /history/ ──────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=Union[SimpleHistoryResponse, GoalHistoryResponse]
)
def get_history(
    *,
    email: str = Query(..., description="Correo del usuario"),
    period: Literal["1", "6", "12", "36", "60"] = Query(
        12,
        description="Meses atrás para el histórico (1, 6, 12, 36 o 60)."
    ),
    data_type: Literal[
        "income", "expenses", "savings", "investments",
        "expense_goals", "saving_goals", "investment_goals"
    ] = Query(
        ...,
        description="Tipo de datos: 'income', 'expenses', 'savings', 'investments', "
                    "'expense_goals', 'saving_goals' o 'investment_goals'."
    ),
    session: Session = Depends(get_session),
):
    stmt_user = select(User).where(User.email == email)
    user = session.exec(stmt_user).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user_id = user.id

    start_date: pydate = _compute_start_date(period)

    if data_type in {"income", "expenses", "savings", "investments"}:
        model_map = {
            "income": Income,
            "expenses": Expense,
            "savings": Saving,
            "investments": Investment,
        }
        Model = model_map[data_type]

        stmt = (
            select(
                extract("year", Model.date).label("year"),
                extract("month", Model.date).label("month"),
                func.coalesce(func.sum(Model.amount), 0).label("total"),
            )
            .where(
                Model.user_id == user_id,
                Model.date >= start_date
            )
            .group_by(
                extract("year", Model.date),
                extract("month", Model.date)
            )
            .order_by(
                extract("year", Model.date),
                extract("month", Model.date)
            )
        )
        rows = session.exec(stmt).all()

        entries = [
            SimpleHistoryEntry(
                year=int(r.year),
                month=int(r.month),
                total=float(r.total),
            )
            for r in rows
        ]

        if entries:
            total_sum = sum(entry.total for entry in entries)
            average = round(total_sum / len(entries), 2)
        else:
            total_sum = 0.0
            average = 0.0

        return SimpleHistoryResponse(
            entries=entries,
            total_sum=total_sum,
            average=average
        )

    else:
        goal_map = {
            "expense_goals": (ExpenseGoal, Expense),
            "saving_goals": (SavingGoal, Saving),
            "investment_goals": (InvestmentGoal, Investment),
        }
        GoalModel, ActualModel = goal_map[data_type]

        stmt_goals = (
            select(
                extract("year", GoalModel.date).label("year"),
                extract("month", GoalModel.date).label("month"),
                GoalModel.value.label("goal_percentage"),
            )
            .where(
                GoalModel.user_id == user_id,
                GoalModel.date >= start_date
            )
            .order_by(extract("year", GoalModel.date), extract("month", GoalModel.date))
        )
        goals_rows = session.exec(stmt_goals).all()

        stmt_incomes = (
            select(
                extract("year", Income.date).label("year"),
                extract("month", Income.date).label("month"),
                func.coalesce(func.sum(Income.amount), 0).label("income"),
            )
            .where(
                Income.user_id == user_id,
                Income.date >= start_date
            )
            .group_by(extract("year", Income.date), extract("month", Income.date))
        )
        income_rows = session.exec(stmt_incomes).all()

        stmt_actuals = (
            select(
                extract("year", ActualModel.date).label("year"),
                extract("month", ActualModel.date).label("month"),
                func.coalesce(func.sum(ActualModel.amount), 0).label("actual_sum"),
            )
            .where(
                ActualModel.user_id == user_id,
                ActualModel.date >= start_date
            )
            .group_by(extract("year", ActualModel.date), extract("month", ActualModel.date))
        )
        actual_rows = session.exec(stmt_actuals).all()

        income_map = {(int(r.year), int(r.month)): float(r.income) for r in income_rows}
        actual_map = {(int(r.year), int(r.month)): float(r.actual_sum) for r in actual_rows}

        entries = []
        met_count = 0

        for row in goals_rows:
            yr = int(row.year)
            mo = int(row.month)
            percentage = float(row.goal_percentage) / 100
            income = income_map.get((yr, mo), 0.0)
            goal_value = round(income * percentage, 2)
            actual_value = actual_map.get((yr, mo), 0.0)
            met_flag = actual_value >= goal_value
            if met_flag:
                met_count += 1
            entries.append(GoalHistoryEntry(
                year=yr,
                month=mo,
                goal_value=goal_value,
                actual_value=actual_value,
                met=met_flag
            ))

        total_goal_value = round(sum(e.goal_value for e in entries), 2)
        average_goal_value = round(total_goal_value / len(entries), 2) if entries else 0.0
        goal_met_percentage = round((met_count / len(entries)) * 100, 1) if entries else 0.0

        return GoalHistoryResponse(
            entries=entries,
            total_goal_value=total_goal_value,
            average_goal_value=average_goal_value,
            goal_met_percentage=goal_met_percentage
        )