from sqlmodel import select
from app.models.user import Expense, Subscription, Budget, Income


def get_dashboard_data(db, user_id: int):
    expenses = db.exec(select(Expense).where(Expense.user_id == user_id)).all()
    subs = db.exec(select(Subscription).where(Subscription.user_id == user_id)).all()
    budgets = db.exec(select(Budget).where(Budget.user_id == user_id)).all()
    income = db.exec(select(Income).where(Income.user_id == user_id)).first()

    total_expenses = sum(e.amount for e in expenses)
    total_subs = sum(
        s.amount if s.billing_cycle == "monthly" else s.amount / 12
        for s in subs
    )

    return {
        "income": income.amount if income else 0,
        "transactions": len(expenses),
        "active_subs": len(subs),
        "budget_items": len(budgets),
        "total_expenses": total_expenses,
        "total_subscriptions": total_subs,
    }