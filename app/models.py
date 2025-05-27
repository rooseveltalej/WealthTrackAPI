from typing import Optional
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    email: str = Field(..., unique=True, index=True, max_length=255)
    username: Optional[str] = Field(None, max_length=50)

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str = Field(..., max_length=255)

class UserRead(UserBase):
    id: int