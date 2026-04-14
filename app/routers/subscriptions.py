from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import select
from datetime import date

from app.models.user import Subscription, BillingCycle, Category
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep

router = APIRouter()


# -------------------------
# CREATE SUBSCRIPTION
# -------------------------
@router.post("/subscriptions/create")
async def create_subscription(
    user: AuthDep,
    db: SessionDep,
    service_name: str = Form(...),
    amount: float = Form(...),
    billing_cycle: str = Form(...),
    next_billing_date: date = Form(...),
    category: str = Form(...)
):
    sub = Subscription(
        service_name=service_name,
        amount=amount,
        billing_cycle=billing_cycle,
        next_billing_date=next_billing_date,
        category=category,
        user_id=user.id
    )

    db.add(sub)
    db.commit()

    return RedirectResponse("/subscriptions", status_code=303)


# -------------------------
# DELETE SUBSCRIPTION
# -------------------------
@router.post("/subscriptions/delete/{sub_id}")
async def delete_subscription(
    sub_id: int,
    user: AuthDep,
    db: SessionDep
):
    sub = db.get(Subscription, sub_id)

    if sub and sub.user_id == user.id:
        db.delete(sub)
        db.commit()

    return RedirectResponse("/subscriptions", status_code=303)