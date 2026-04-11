from sqlmodel import SQLModel, Field
from typing import Optional


class Budget(SQLModel, table=True):
    id:     Optional[int] = Field(default=None, primary_key=True)
    name:   str
    amount: float
    color:  str
    icon:   str
    spent:  float = 0.0
