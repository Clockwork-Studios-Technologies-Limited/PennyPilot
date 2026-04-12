# from sqlmodel import select
# from app.models.Expenses import Budget


# class BudgetRepository:
#     def __init__(self, db):
#         self.db = db

#     def get_all(self):
#         return self.db.exec(select(Budget)).all()

#     def get_by_id(self, budget_id: int):
#         return self.db.get(Budget, budget_id)

#     def create(self, budget: Budget):
#         self.db.add(budget)
#         self.db.commit()
#         self.db.refresh(budget)
#         return budget

#     def delete(self, budget: Budget):
#         self.db.delete(budget)
#         self.db.commit()
