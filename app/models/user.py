from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from pydantic import EmailStr
from datetime import date
from enum import Enum

# -------------------------
# ENUMS
# -------------------------
class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserTag(str, Enum):
    stable = "stable"
    very_safe = "very_safe"
    risky = "risky"
    critical = "critical"
    no_tag = "no_tag"


# -------------------------
# BASE (shared fields)
# -------------------------
class UserBase(SQLModel):
    username: str
    email: EmailStr


# -------------------------
# CREATE SCHEMA (input)
# -------------------------
class UserCreate(UserBase):
    password: str


# -------------------------
# TABLE MODEL (DB)
# -------------------------
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    hashed_password: str

    role: UserRole = Field(default=UserRole.user)
    tag: Optional[UserTag] = None

    income: Optional["Income"] = Relationship(back_populates="user")
    expenses: List["Expense"] = Relationship(back_populates="user")
    subscriptions: List["Subscription"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    
class Category(str, Enum):
    food = "Food & Dining"
    transport = "Transportation"
    entertainment = "Entertainment"
    utilities = "Bills & Utilities"
    shopping = "Shopping"
    rent = "Rent"
    shopping_items = "Shopping"
    health = "Health"
    savings = "Savings"
    other = "Other"
    
    
class Income(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float

    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="income")
    
class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    amount: float
    date: date
    category: Category

    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="expenses")
    
class BillingCycle(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    service_name: str
    amount: float
    billing_cycle: BillingCycle
    next_billing_date: date
    category: Category

    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="subscriptions")

class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    category: Category
    monthly_limit: float

    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="budgets")
    
# class Budget(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)

#     category: Category
#     monthly_limit: float

#     user_id: int = Field(foreign_key="user.id")
#     user: Optional["User"] = Relationship(back_populates="budgets")

