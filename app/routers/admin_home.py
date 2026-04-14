from fastapi import APIRouter, Form, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates


# @router.get("/admin/dashboard", response_class=HTMLResponse)
# async def admin_home_view(
#     request: Request,
#     user: AdminDep,
#     db: SessionDep
# ):
#     return templates.TemplateResponse(
#         request=request,
#         name="Admin/admin-panel.html",
#         context={"user": user}
#     )
from sqlmodel import select
from math import ceil

from app.models.user import Budget, User, Income, Expense, Subscription, UserTag, UserRole
from sqlmodel import select


# -------------------------
# LIST USERS (PAGINATED)
# -------------------------
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    page: int = 1,
    limit: int = 10
):
    offset = (page - 1) * limit

    users = db.exec(select(User).offset(offset).limit(limit)).all()
    users = [u for u in users if u.role != UserRole.admin]
    total_users = len(users)

    enriched_users = []

    for u in users:
        income = db.exec(select(Income).where(Income.user_id == u.id)).first()

        expenses = db.exec(select(Expense).where(Expense.user_id == u.id)).all()
        subs = db.exec(select(Subscription).where(Subscription.user_id == u.id)).all()

        monthly_income = income.amount if income else 0

        monthly_expenses = sum(e.amount for e in expenses)

        monthly_subs = sum(
            s.amount if s.billing_cycle == "monthly" else s.amount / 12
            for s in subs
        )

        total_spend = monthly_expenses + monthly_subs

        burn_rate = (
            round((total_spend / monthly_income) * 100, 1)
            if monthly_income > 0 else 0
        )

        enriched_users.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "income": monthly_income,
            "tag": u.tag,
            "burn_rate": burn_rate,
        })

    total_pages = max(1, ceil(total_users / limit))

    # tag stats
    tag_counts = {
        "very_safe": len([u for u in users if u.tag == UserTag.very_safe]),
        "stable": len([u for u in users if u.tag == UserTag.stable]),
        "risky": len([u for u in users if u.tag == UserTag.risky]),
        "critical": len([u for u in users if u.tag == UserTag.critical]),
    }

    # return templates.TemplateResponse(
    #     "Admin/admin-panel.html",
    #     {
    #         "request": request,
    #         "user": user,
    #         "users": enriched_users,
    #         "page": page,
    #         "total_pages": total_pages,
    #         "total_users": total_users,
    #         "tag_counts": tag_counts
    #     }
    # )
    return templates.TemplateResponse(
        request=request,
        name="Admin/admin-panel.html",
        context={"user": user,
                 "users": enriched_users,
                 "page": page,
                 "total_pages": total_pages,
                 "total_users": total_users,
                 "tag_counts": tag_counts,
                }
    )

# -------------------------
# UPDATE USER TAG
# -------------------------
@router.post("/admin/user/tag")
async def update_user_tag(
    user_id: int = Form(...),
    tag: UserTag = Form(...),
    db: SessionDep = SessionDep,
    admin: AdminDep = AdminDep
):
    user = db.get(User, user_id)

    if not user:
        return RedirectResponse("/admin/dashboard", status_code=303)

    user.tag = tag
    db.add(user)
    db.commit()

    return RedirectResponse("/admin/dashboard", status_code=303)


# -------------------------
# DELETE USER
# -------------------------
# @router.post("/admin/user/delete")
# async def delete_user(
#     user_id: int = Form(...),
#     db: SessionDep = SessionDep,
#     admin: AdminDep = AdminDep
# ):
#     user = db.get(User, user_id)

#     if user:
#         db.delete(user)
#         db.commit()

#     return RedirectResponse("/admin/dashboard", status_code=303)

from sqlmodel import select

@router.post("/admin/user/delete")
async def delete_user(db: SessionDep, admin: AdminDep, user_id: int = Form(...),):

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # --- DELETE RELATED DATA FIRST ---
    # Income (one-to-one)
    if user.income:
        db.delete(user.income)

    # Expenses
    expenses = db.exec(select(Expense).where(Expense.user_id == user_id)).all()
    for e in expenses:
        db.delete(e)

    # Subscriptions
    subs = db.exec(select(Subscription).where(Subscription.user_id == user_id)).all()
    for s in subs:
        db.delete(s)

    # Budgets
    budgets = db.exec(select(Budget).where(Budget.user_id == user_id)).all()
    for b in budgets:
        db.delete(b)

    # --- NOW DELETE USER ---
    db.delete(user)

    db.commit()
    
    return RedirectResponse("/admin/dashboard", status_code=303)