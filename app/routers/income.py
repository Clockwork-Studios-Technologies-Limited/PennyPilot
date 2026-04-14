from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.user import Income
from sqlmodel import select

router = APIRouter()

@router.post("/income/set")
async def add_income(
    db: SessionDep,
    user: AuthDep,
    next: str = Form("/dashboard"),
    amount: float = Form(...),
):
    existing = db.exec(
        select(Income).where(Income.user_id == user.id)
    ).first()

    if existing:
        existing.amount = amount
        db.add(existing)
    else:
        new_income = Income(amount=amount, user_id=user.id)
        db.add(new_income)

    db.commit()

    return RedirectResponse(url=next, status_code=303)
