from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from app.services.dashboard_data import get_dashboard_data
from . import router, templates


# @router.get("/dashboard", response_class=HTMLResponse)
# async def dashboard_view(
#     request: Request,
#     user: AuthDep,
#     db: SessionDep
# ):
#     return templates.TemplateResponse(
#         request=request,
#         name="App/dashboard.html",
#         context={"user": user}
#     )
from sqlmodel import select
from app.models.user import Expense, Subscription, Budget

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    expenses = db.exec(
        select(Expense).where(Expense.user_id == user.id)
    ).all()

    subs = db.exec(
        select(Subscription).where(Subscription.user_id == user.id)
    ).all()

    budgets = db.exec(
        select(Budget).where(Budget.user_id == user.id)
    ).all()

    # -------------------------
    # income
    # -------------------------
    income = user.income.amount if user.income else 0

    # -------------------------
    # financials
    # -------------------------
    one_time = sum(e.amount for e in expenses)

    subs_monthly = sum(
        s.amount if s.billing_cycle == "monthly" else s.amount / 12
        for s in subs
    )

    total_spent = one_time + subs_monthly
    remaining = income - total_spent

    burn_rate = (total_spent / income * 100) if income else 0
    daily_avg = total_spent / 30 if total_spent else 0

    return templates.TemplateResponse(
        request=request,
        name="App/dashboard.html",
        context={
            "user": user,

            # income
            "income": round(income, 2),

            # stats
            "transactions": len(expenses),
            "subs_count": len(subs),
            "budget_count": len(budgets),

            # financials
            "one_time": round(one_time, 2),
            "subs_total": round(subs_monthly, 2),
            "total_spent": round(total_spent, 2),
            "remaining": round(remaining, 2),

            # burn
            "burn_rate": round(burn_rate, 1),
            "daily_avg": round(daily_avg, 2)
        }
    )
    
# @router.get("/expenses", response_class=HTMLResponse)
# async def expenses_view(
#     request: Request,
#     user: AuthDep,
#     db: SessionDep
# ):
#     return templates.TemplateResponse(
#         request=request,
#         name="App/expenses.html",
#         context={"user": user}
#     )
from sqlmodel import select
from app.models.user import Expense, Category
from sqlalchemy import func
@router.get("/expenses", response_class=HTMLResponse)
async def expenses_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = 1
):
    page_size = 5

    all_expenses = db.exec(
        select(Expense)
        .where(Expense.user_id == user.id)
        .order_by(Expense.date.desc())
    ).all()
    
    total_amount = sum(e.amount for e in all_expenses)
    avg_amount = total_amount / len(all_expenses) if len(all_expenses) > 0 else 0

    total = len(all_expenses)
    total_pages = max((total + page_size - 1) // page_size, 1)

    start = (page - 1) * page_size
    end = start + page_size

    paginated = all_expenses[start:end]
    
    # Transform expenses to show category values instead of enum
    expenses_display = []
    for e in paginated:
        expenses_display.append({
            "id": e.id,
            "name": e.name,
            "amount": e.amount,
            "category": e.category.value,
            "date": e.date,
        })
    
    stats = get_dashboard_data(db, user.id)


    return templates.TemplateResponse(
        request=request,
        name="App/expenses.html",
        context={
            "user": user,
            "expenses": expenses_display,
            "page": page,
            "total_pages": total_pages,
            "categories": list(Category),
            "total_expenses": round(total_amount, 0),
            "transaction_count": total,
            "avg_expense": round(avg_amount, 2),
            "stats": stats,
        }
    )


# @router.get("/subscriptions", response_class=HTMLResponse)
# async def subscriptions_view(
#     request: Request,
#     user: AuthDep,
#     db: SessionDep
# ):
#     return templates.TemplateResponse(
#         request=request,
#         name="App/subscriptions.html",
#         context={"user": user}
#     )
from sqlmodel import select
from app.models.user import Subscription, BillingCycle

@router.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = 1
):
    page_size = 5

    subs = db.exec(
        select(Subscription)
        .where(Subscription.user_id == user.id)
        .order_by(Subscription.next_billing_date)
    ).all()

    total = len(subs)
    total_pages = max((total + page_size - 1) // page_size, 1)

    start = (page - 1) * page_size
    paginated = subs[start:start + page_size]

    # -------------------------
    # STATS CALCULATION
    # -------------------------
    monthly_total = sum(
        s.amount if s.billing_cycle == "monthly" else s.amount / 12
        for s in subs
    )

    yearly_total = sum(
        s.amount if s.billing_cycle == "yearly" else s.amount * 12
        for s in subs
    )

    daily_avg = monthly_total / 30 if monthly_total else 0
    
    
    stats = get_dashboard_data(db, user.id)

    return templates.TemplateResponse(
        request=request,
        name="App/subscriptions.html",
        context={
            "user": user,
            "subs": paginated,
            "page": page,
            "total_pages": total_pages,

            # enums
            "categories": list(Category),
            "billing_cycles": list(BillingCycle),

            # stats
            "monthly_total": round(monthly_total, 2),
            "yearly_total": round(yearly_total, 2),
            "daily_avg": round(daily_avg, 2),
            "active_count": total,
            "stats": stats
        }
    )
    
    
    
# @router.get("/budgets", response_class=HTMLResponse)
# async def budget_view(
#     request: Request,
#     user: AuthDep,
#     db: SessionDep
# ):
#     return templates.TemplateResponse(
#         request=request,
#         name="App/budget.html",
#         context={
#             "user": user
#         }
#     )
from sqlmodel import select
from app.models.user import Budget, Expense, Subscription, Category

@router.get("/budgets", response_class=HTMLResponse)
async def budget_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = 1
):
    page_size = 5

    budgets = db.exec(
        select(Budget)
        .where(Budget.user_id == user.id)
    ).all()

    expenses = db.exec(
        select(Expense)
        .where(Expense.user_id == user.id)
    ).all()

    subs = db.exec(
        select(Subscription)
        .where(Subscription.user_id == user.id)
    ).all()

    # -------------------------
    # convert subs → monthly equivalent
    # -------------------------
    def sub_monthly(s):
        return s.amount if s.billing_cycle == "monthly" else s.amount / 12

    # -------------------------
    # CATEGORY SPENDING MAP
    # -------------------------
    spent_map = {}

    for e in expenses:
        spent_map[e.category] = spent_map.get(e.category, 0) + e.amount

    for s in subs:
        spent_map[s.category] = spent_map.get(s.category, 0) + sub_monthly(s)

    # -------------------------
    # ENRICH BUDGETS
    # -------------------------
    enriched = []
    total_budget = 0
    total_spent = 0

    for b in budgets:
        spent = spent_map.get(b.category, 0)
        remaining = b.monthly_limit - spent

        enriched.append({
            "id": b.id,
            "category": b.category.value,
            "limit": b.monthly_limit,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percent": round((spent / b.monthly_limit) * 100, 1) if b.monthly_limit else 0
        })

        total_budget += b.monthly_limit
        total_spent += spent

    total_remaining = total_budget - total_spent

    # pagination
    total = len(enriched)
    total_pages = max((total + page_size - 1) // page_size, 1)

    start = (page - 1) * page_size
    paginated = enriched[start:start + page_size]
    
    one_time_total = sum(e.amount for e in expenses)

    subscription_total = sum(
        s.amount if s.billing_cycle == "monthly" else s.amount / 12
        for s in subs
    )
    
    health = []
    
    for b in budgets:
        spent = spent_map.get(b.category, 0)

        pct = (spent / b.monthly_limit * 100) if b.monthly_limit else 0

        if pct >= 100:
            status = "over"
        elif pct >= 75:
            status = "warning"
        else:
            status = "safe"

        health.append({
            "category": b.category.value,
            "spent": round(spent, 2),
            "limit": b.monthly_limit,
            "pct": round(pct, 1),
            "status": status,
        })

    breakdown_total = one_time_total + subscription_total

    # category health
    categories_used = len(budgets)
    
    raw_pct = (total_spent / total_budget * 100) if total_budget else 0
    overall_pct = round(raw_pct, 2)

    stats = get_dashboard_data(db, user.id)


    return templates.TemplateResponse(
        request=request,
        name="App/budget.html",
        context={
            "user": user,
            "budgets": paginated,
            "page": page,
            "total_pages": total_pages,

            "categories": list(Category),

            "total_budget": round(total_budget, 2),
            "total_spent": round(total_spent, 2),
            "total_remaining": round(total_remaining, 2),

            "category_count": categories_used,
            
            "one_time_total": round(one_time_total, 2),
            "subscription_total": round(subscription_total, 2),
            "breakdown_total": round(breakdown_total, 2),

            "health": health,
            "overall_pct": overall_pct,
            "stats": stats,
        }
    )


@router.get("/reports", response_class=HTMLResponse)
async def reports_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    spending_page: int = 1,
    budget_page: int = 1
):
    from datetime import datetime, timedelta
    from app.models.user import Expense, Subscription, Budget, Income
    
    # Helper function to determine color based on percentage
    def get_color_by_percentage(pct):
        if pct <= 30:
            return {"color": "#2ecc71", "gradient_start": "#2ecc71", "gradient_end": "#27ae60"}  # Green
        elif pct <= 50:
            return {"color": "#3498db", "gradient_start": "#3498db", "gradient_end": "#2980b9"}  # Blue
        elif pct <= 80:
            return {"color": "#f39c12", "gradient_start": "#f39c12", "gradient_end": "#d68910"}  # Orange
        else:
            return {"color": "#e74c3c", "gradient_start": "#e74c3c", "gradient_end": "#c0392b"}  # Red
    
    stats = get_dashboard_data(db, user.id)
    page_size = 5
    
    # Get all expenses
    expenses = db.exec(
        select(Expense).where(Expense.user_id == user.id)
    ).all()
    
    # Get all subscriptions
    subs = db.exec(
        select(Subscription).where(Subscription.user_id == user.id)
    ).all()
    
    # Get all budgets
    budgets = db.exec(
        select(Budget).where(Budget.user_id == user.id)
    ).all()
    
    # Get income
    income_obj = db.exec(
        select(Income).where(Income.user_id == user.id)
    ).first()
    
    # --------- CALCULATE TOTALS ---------
    total_expenses = sum(e.amount for e in expenses)
    monthly_sub_cost = sum(
        s.amount if s.billing_cycle == "monthly" else s.amount / 12
        for s in subs
    )
    total_spending = total_expenses + monthly_sub_cost
    income = income_obj.amount if income_obj else 0
    
    # --------- SUMMARY CARDS ---------
    net_savings = income - total_spending
    savings_rate = ((income - total_spending) / income * 100) if income > 0 else 0
    daily_avg = total_spending / 30 if total_spending > 0 else 0
    largest_expense = max((e.amount for e in expenses), default=0)
    
    # --------- SPENDING BY CATEGORY ---------
    category_spending = {}
    for e in expenses:
        cat = e.category.value
        category_spending[cat] = category_spending.get(cat, 0) + e.amount
    
    for s in subs:
        cat = s.category.value
        monthly = s.amount if s.billing_cycle == "monthly" else s.amount / 12
        category_spending[cat] = category_spending.get(cat, 0) + monthly
    
    # Create spending by category list with percentages and colors
    spending_by_cat_all = []
    for cat, amount in sorted(category_spending.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / total_spending * 100) if total_spending > 0 else 0
        color = get_color_by_percentage(pct)
        spending_by_cat_all.append({
            "category": cat,
            "amount": round(amount, 2),
            "percent": round(pct, 1),
            "color": color["color"],
            "gradient_start": color["gradient_start"],
            "gradient_end": color["gradient_end"]
        })
    
    # --------- BUDGET VS ACTUAL ---------
    budget_vs_actual_all = []
    for b in budgets:
        cat_str = b.category.value
        spent = category_spending.get(cat_str, 0)
        remaining = b.monthly_limit - spent
        pct = (spent / b.monthly_limit * 100) if b.monthly_limit > 0 else 0
        color = get_color_by_percentage(pct)
        
        budget_vs_actual_all.append({
            "category": cat_str,
            "spent": round(spent, 2),
            "budget": round(b.monthly_limit, 2),
            "remaining": round(remaining, 2),
            "percent": round(pct, 1),
            "color": color["color"],
            "gradient_start": color["gradient_start"],
            "gradient_end": color["gradient_end"]
        })
    
    # --------- PAGINATION FOR SPENDING BY CATEGORY ---------
    total_spending_items = len(spending_by_cat_all)
    total_spending_pages = max((total_spending_items + page_size - 1) // page_size, 1)
    
    spending_start = (spending_page - 1) * page_size
    spending_end = spending_start + page_size
    spending_by_cat_paginated = spending_by_cat_all[spending_start:spending_end]
    
    # --------- PAGINATION FOR BUDGET VS ACTUAL ---------
    total_budget_items = len(budget_vs_actual_all)
    total_budget_pages = max((total_budget_items + page_size - 1) // page_size, 1)
    
    budget_start = (budget_page - 1) * page_size
    budget_end = budget_start + page_size
    budget_vs_actual_paginated = budget_vs_actual_all[budget_start:budget_end]
    
    # --------- MONTHLY SPENDING TREND (last 12 months) ---------
    today = datetime.now().date()
    monthly_data = {}
    
    # Initialize last 12 months
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_key = month_date.strftime("%B")
        monthly_data[month_key] = 0
    
    # Add expenses to monthly data
    for e in expenses:
        month_key = e.date.strftime("%B")
        if month_key in monthly_data:
            monthly_data[month_key] += e.amount
    
    # Add subscriptions to monthly data
    for s in subs:
        month_key = s.next_billing_date.strftime("%B")
        monthly_amt = s.amount if s.billing_cycle == "monthly" else s.amount / 12
        if month_key in monthly_data:
            monthly_data[month_key] += monthly_amt
    
    # Sort by calendar month order (January through December)
    month_order = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    sorted_data = {month: monthly_data[month] for month in month_order if month in monthly_data}
    
    monthly_labels = list(sorted_data.keys())
    monthly_values = [round(v, 2) for v in sorted_data.values()]

    return templates.TemplateResponse(
        request=request,
        name="App/reports.html",
        context={
            "user": user,
            "stats": stats,
            "savings_rate": round(savings_rate, 1),
            "total_spending": round(total_spending, 2),
            "daily_average": round(daily_avg, 2),
            "largest_expense": round(largest_expense, 2),
            "spending_by_category": spending_by_cat_paginated,
            "spending_page": spending_page,
            "spending_total_pages": total_spending_pages,
            "budget_vs_actual": budget_vs_actual_paginated,
            "budget_page": budget_page,
            "budget_total_pages": total_budget_pages,
            "income": round(income, 2),
            "total_expenses": round(total_expenses, 2),
            "sub_cost": round(monthly_sub_cost, 2),
            "net_savings": round(net_savings, 2),
            "monthly_labels": monthly_labels,
            "monthly_values": monthly_values,
            "active_subs": len(subs),
        }
    )