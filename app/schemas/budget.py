from pydantic import BaseModel


class BudgetCreate(BaseModel):
    name:   str
    amount: float
    color:  str
    icon:   str = "💰"
