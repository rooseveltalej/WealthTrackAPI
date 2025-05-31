# app/routers/dashboard.py

from datetime import date as pydate
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body
from sqlalchemy import func, extract
from sqlmodel import Session, select
from pydantic import BaseModel

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
    prefix="/dashboard",
    tags=["dashboard"],
)


def _get_year_month(target_date: pydate) -> (int, int):
    return target_date.year, target_date.month


class DashboardRequest(BaseModel):
    email: str


@router.get("/", response_model=dict)
def get_dashboard_data_by_body(
    *,
    payload: DashboardRequest = Body(...),
    session: Session = Depends(get_session),
):
    """
    Devuelve datos de finanzas del usuario cuyo email llegue en el body para el mes actual:
      - Totales: ingreso, gasto, ahorro, inversión
      - Porcentaje de metas: gasto, ahorro, inversión
      - Listados: expenses, savings, investments
      - Distribuciones por categoría: categoryExpenses, categorySavings, categoryInvestments

    Body JSON esperado:
    {
      "email": "usuario@ejemplo.com"
    }
    """
    # 1) Obtener el usuario por email
    stmt_user = select(User).where(User.email == payload.email)
    user = session.exec(stmt_user).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_id = user.id

    # 2) Determinar año y mes actuales
    today = pydate.today()
    year, month = _get_year_month(today)

    # 3) Ingreso mensual total
    stmt_income = (
        select(func.coalesce(func.sum(Income.amount), 0))
        .where(
            Income.user_id == user_id,
            extract("year", Income.date) == year,
            extract("month", Income.date) == month,
        )
    )
    income_total = session.exec(stmt_income).one()

    # 4) Gasto mensual total
    stmt_expense = (
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(
            Expense.user_id == user_id,
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
    )
    expense_total = session.exec(stmt_expense).one()

    # 5) Ahorro mensual total
    stmt_saving = (
        select(func.coalesce(func.sum(Saving.amount), 0))
        .where(
            Saving.user_id == user_id,
            extract("year", Saving.date) == year,
            extract("month", Saving.date) == month,
        )
    )
    saving_total = session.exec(stmt_saving).one()

    # 6) Inversión mensual total
    stmt_invest = (
        select(func.coalesce(func.sum(Investment.amount), 0))
        .where(
            Investment.user_id == user_id,
            extract("year", Investment.date) == year,
            extract("month", Investment.date) == month,
        )
    )
    investment_total = session.exec(stmt_invest).one()

    # 7) Porcentaje meta de gasto
    stmt_expense_goal = (
        select(ExpenseGoal.value)
        .where(
            ExpenseGoal.user_id == user_id,
            extract("year", ExpenseGoal.date) == year,
            extract("month", ExpenseGoal.date) == month,
        )
    )
    result_expense_goal = session.exec(stmt_expense_goal).one_or_none()
    expense_goal_percent = float(result_expense_goal) if result_expense_goal else 0.0

    # 8) Porcentaje meta de ahorro
    stmt_saving_goal = (
        select(SavingGoal.value)
        .where(
            SavingGoal.user_id == user_id,
            extract("year", SavingGoal.date) == year,
            extract("month", SavingGoal.date) == month,
        )
    )
    result_saving_goal = session.exec(stmt_saving_goal).one_or_none()
    saving_goal_percent = float(result_saving_goal) if result_saving_goal else 0.0

    # 9) Porcentaje meta de inversión
    stmt_invest_goal = (
        select(InvestmentGoal.value)
        .where(
            InvestmentGoal.user_id == user_id,
            extract("year", InvestmentGoal.date) == year,
            extract("month", InvestmentGoal.date) == month,
        )
    )
    result_invest_goal = session.exec(stmt_invest_goal).one_or_none()
    investment_goal_percent = float(result_invest_goal) if result_invest_goal else 0.0

    # 10) Listado de gastos individuales
    stmt_expenses_list = (
        select(Expense)
        .where(
            Expense.user_id == user_id,
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
    )
    expenses_rows = session.exec(stmt_expenses_list).all()
    expenses_list = [
        {"date": e.date.isoformat(), "amount": float(e.amount), "category": e.category}
        for e in expenses_rows
    ]

    # 11) Listado de ahorros individuales
    stmt_savings_list = (
        select(Saving)
        .where(
            Saving.user_id == user_id,
            extract("year", Saving.date) == year,
            extract("month", Saving.date) == month,
        )
    )
    savings_rows = session.exec(stmt_savings_list).all()
    savings_list = [
        {"date": s.date.isoformat(), "amount": float(s.amount), "category": s.category}
        for s in savings_rows
    ]

    # 12) Listado de inversiones individuales
    stmt_investments_list = (
        select(Investment)
        .where(
            Investment.user_id == user_id,
            extract("year", Investment.date) == year,
            extract("month", Investment.date) == month,
        )
    )
    investments_rows = session.exec(stmt_investments_list).all()
    investments_list = [
        {"date": i.date.isoformat(), "amount": float(i.amount), "category": i.category}
        for i in investments_rows
    ]

    # 13) Distribución de gastos por categoría
    stmt_cat_expenses = (
        select(
            Expense.category,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .where(
            Expense.user_id == user_id,
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
        .group_by(Expense.category)
    )
    cat_expenses_rows = session.exec(stmt_cat_expenses).all()
    category_expenses = [
        {"category": row.category, "total": float(row.total)} for row in cat_expenses_rows
    ]

    # 14) Distribución de ahorros por categoría
    stmt_cat_savings = (
        select(
            Saving.category,
            func.coalesce(func.sum(Saving.amount), 0).label("total"),
        )
        .where(
            Saving.user_id == user_id,
            extract("year", Saving.date) == year,
            extract("month", Saving.date) == month,
        )
        .group_by(Saving.category)
    )
    cat_savings_rows = session.exec(stmt_cat_savings).all()
    category_savings = [
        {"category": row.category, "total": float(row.total)} for row in cat_savings_rows
    ]

    # 15) Distribución de inversiones por categoría
    stmt_cat_invests = (
        select(
            Investment.category,
            func.coalesce(func.sum(Investment.amount), 0).label("total"),
        )
        .where(
            Investment.user_id == user_id,
            extract("year", Investment.date) == year,
            extract("month", Investment.date) == month,
        )
        .group_by(Investment.category)
    )
    cat_invests_rows = session.exec(stmt_cat_invests).all()
    category_investments = [
        {"category": row.category, "total": float(row.total)} for row in cat_invests_rows
    ]

    # 16) Armar payload final
    dashboard_payload = {
        "incomeTotal": float(income_total),
        "expenseTotal": float(expense_total),
        "savingTotal": float(saving_total),
        "investmentTotal": float(investment_total),
        "expenseGoalPercent": expense_goal_percent,
        "savingGoalPercent": saving_goal_percent,
        "investmentGoalPercent": investment_goal_percent,
        "expenses": expenses_list,
        "savings": savings_list,
        "investments": investments_list,
        "categoryExpenses": category_expenses,
        "categorySavings": category_savings,
        "categoryInvestments": category_investments,
    }

    return dashboard_payload

