# app/models.py

from typing import Optional
from datetime import date as pydate
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Numeric, Column, String, Integer, Date

# ─── Users ────────────────────────────────────────────────────────────────────
class UserBase(SQLModel):
    email: str                = Field(..., unique=True, index=True, max_length=255)
    username: Optional[str]   = Field(None, max_length=50)

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str     = Field(..., max_length=255)

class UserRead(UserBase):
    id: int

class UserCreate(UserBase):
    password: str



class Income(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: pydate
    user_id: int = Field(foreign_key="users.id")
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))

class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True) 
    date: pydate
    user_id: int = Field(foreign_key="users.id")
    amount: Decimal = Field(sa_column=Column("amount", Numeric(10, 2), nullable=False))
    category: str = Field(sa_column=Column("category", String(100), nullable=False))

class Saving(SQLModel, table=True):
    __tablename__ = "savings"
    id: Optional[int] = Field(default=None, primary_key=True)
    date: pydate
    user_id: int = Field(foreign_key="users.id")
    amount: Decimal = Field(sa_column=Column("amount", Numeric(10, 2), nullable=False))
    category: str = Field(sa_column=Column("category", String(100), nullable=False))

class Investment(SQLModel, table=True):
    __tablename__ = "investments"
    id: Optional[int] = Field(default=None, primary_key=True)
    date: pydate
    user_id: int = Field(foreign_key="users.id")
    amount: Decimal = Field(sa_column=Column("amount", Numeric(10, 2), nullable=False))
    category: str = Field(sa_column=Column("category", String(100), nullable=False))


class ExpenseGoal(SQLModel, table=True):
    __tablename__ = "expensegoals"
    date: pydate = Field(sa_column=Column("date", Date, primary_key=True))
    user_id: int = Field(sa_column=Column("userid", Integer, primary_key=True))
    value: Decimal = Field(sa_column=Column("value", Numeric(5, 2), nullable=False))

class SavingGoal(SQLModel, table=True):
    __tablename__ = "savinggoals"
    date: pydate = Field(sa_column=Column("date", Date, primary_key=True))
    user_id: int = Field(sa_column=Column("userid", Integer, primary_key=True))
    value: Decimal = Field(sa_column=Column("value", Numeric(5, 2), nullable=False))


class InvestmentGoal(SQLModel, table=True):
    __tablename__ = "investmentgoals"
    date: pydate = Field(sa_column=Column("date", Date, primary_key=True))
    user_id: int = Field(sa_column=Column("userid", Integer, primary_key=True))
    value: Decimal = Field(sa_column=Column("value", Numeric(5, 2), nullable=False))
