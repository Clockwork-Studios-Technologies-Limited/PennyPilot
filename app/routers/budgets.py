from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from sqlmodel import select

from app.models.user import Budget, Category, Expense, Subscription
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep

router = APIRouter()


# -------------------------
# CREATE BUDGET
# -------------------------
@router.post("/budgets/create")
async def create_budget(
    user: AuthDep,
    db: SessionDep,
    category: str = Form(...),
    monthly_limit: float = Form(...)
):
    # -------------------------
    # CHECK EXISTING BUDGET
    # -------------------------
    existing = db.exec(
        select(Budget).where(
            Budget.user_id == user.id,
            Budget.category == category
        )
    ).first()

    if existing:
        # 🔥 ADD TO EXISTING
        existing.monthly_limit += monthly_limit
        db.add(existing)

    else:
        # 🆕 CREATE NEW
        budget = Budget(
            category=category,
            monthly_limit=monthly_limit,
            user_id=user.id
        )
        db.add(budget)

    db.commit()

    return RedirectResponse("/budgets", status_code=303)


# -------------------------
# DELETE BUDGET
# -------------------------
@router.post("/budgets/delete/{budget_id}")
async def delete_budget(
    budget_id: int,
    user: AuthDep,
    db: SessionDep
):
    budget = db.get(Budget, budget_id)

    if budget and budget.user_id == user.id:
        db.delete(budget)
        db.commit()

    return RedirectResponse("/budgets", status_code=303)