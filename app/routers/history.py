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


# ─── Función auxiliar para calcular fecha de inicio ───────────────────────────────

def _compute_start_date(period_months):
    period_months = int(period_months)
    today = pydate.today()
    start = today - relativedelta(months=period_months)
    return pydate(year=start.year, month=start.month, day=1)


# ─── Ruta GET /history/ ──────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=Union[SimpleHistoryResponse, List[GoalHistoryEntry]]
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
                GoalModel.value.label("goal_value"),
            )
            .where(
                GoalModel.user_id == user_id,
                GoalModel.date >= start_date
            )
            .order_by(extract("year", GoalModel.date), extract("month", GoalModel.date))
        )
        goals_rows = session.exec(stmt_goals).all()

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


        actual_map = {
            (int(r.year), int(r.month)): float(r.actual_sum) for r in actual_rows
        }

        result: List[GoalHistoryEntry] = []
        for row in goals_rows:
            yr = int(row.year)
            mo = int(row.month)
            gv = float(row.goal_value)
            av = actual_map.get((yr, mo), 0.0)
            met_flag = (av >= gv)
            result.append(
                GoalHistoryEntry(
                    year=yr,
                    month=mo,
                    goal_value=gv,
                    actual_value=av,
                    met=met_flag
                )
            )

        return result