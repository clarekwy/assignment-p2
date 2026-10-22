from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, status

from app.database import initialize_database
from app.repositories import create_expense, list_expenses
from app.schemas import (
    MONTH_PATTERN,
    BudgetCreate,
    BudgetRead,
    BudgetStatus,
    ExpenseCreate,
    ExpenseRead,
)
from app.services import set_monthly_budget


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Expense API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def add_expense(expense: ExpenseCreate) -> ExpenseRead:
    return ExpenseRead.model_validate(create_expense(expense))


@app.get("/expenses", response_model=list[ExpenseRead])
def get_expenses() -> list[ExpenseRead]:
    return [ExpenseRead.model_validate(expense) for expense in list_expenses()]


@app.post("/budgets", response_model=BudgetRead, status_code=status.HTTP_200_OK)
def set_budget(budget: BudgetCreate) -> BudgetRead:
    return BudgetRead.model_validate(set_monthly_budget(budget))


@app.get("/budgets/{month}", response_model=list[BudgetStatus])
def get_budget_summary(
    month: Annotated[str, Path(pattern=MONTH_PATTERN.pattern)],
) -> list[BudgetStatus]:
    return get_budget_status_for_month(month)