from fastapi import HTTPException, status
from app.repositories.budget import BudgetRepository
from app.models.Expenses import Budget
from app.schemas.budget import BudgetCreate


class BudgetService:
    def __init__(self, db):
        self.repo = BudgetRepository(db)

    def get_all(self):
        return self.repo.get_all()

    def create(self, data: BudgetCreate):
        budget = Budget(
            name=data.name,
            amount=data.amount,
            color=data.color,
            icon=data.icon,
        )
        return self.repo.create(budget)

    def delete(self, budget_id: int):
        budget = self.repo.get_by_id(budget_id)
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )
        self.repo.delete(budget)
        return {"message": "Deleted"}
