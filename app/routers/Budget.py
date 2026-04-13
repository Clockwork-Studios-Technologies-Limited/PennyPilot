from app.routers import router, api_router, templates
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
# from app.schemas.budget import BudgetCreate
# from app.services.Budget_service import BudgetService
from fastapi import Request
from fastapi.responses import HTMLResponse




# @api_router.get("/budgets")
# async def get_budgets(user: AuthDep, db: SessionDep):
#     return BudgetService(db).get_all()


# @api_router.post("/budgets")
# async def create_budget(data: BudgetCreate, user: AuthDep, db: SessionDep):
#     return BudgetService(db).create(data)


# @api_router.delete("/budgets/{budget_id}")
# async def delete_budget(budget_id: int, user: AuthDep, db: SessionDep):
#     return BudgetService(db).delete(budget_id)
