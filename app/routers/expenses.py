from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import select
from app.models.user import Expense
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from datetime import date

router = APIRouter()

print("🔥 expenses router LOADED")
# -------------------------
# CREATE EXPENSE
# -------------------------
@router.post("/expenses/create")
async def create_expense(
    user: AuthDep,
    db: SessionDep,
    name: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    date: date = Form(...)
):
    expense = Expense(
        name=name,
        amount=amount,
        category=category,
        date=date,
        user_id=user.id
    )

    db.add(expense)
    db.commit()

    return RedirectResponse("/expenses", status_code=303)


# -------------------------
# DELETE EXPENSE
# -------------------------
@router.post("/expenses/delete/{expense_id}")
async def delete_expense(
    expense_id: int,
    user: AuthDep,
    db: SessionDep
):
    expense = db.get(Expense, expense_id)

    if expense and expense.user_id == user.id:
        db.delete(expense)
        db.commit()

    return RedirectResponse("/expenses", status_code=303)