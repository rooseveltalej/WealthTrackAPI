# app/models.py

from typing import Optional, Annotated
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field

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