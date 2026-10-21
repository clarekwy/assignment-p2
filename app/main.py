from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.database import initialize_database
from app.repositories import create_expense, list_expenses
from app.schemas import ExpenseCreate, ExpenseRead


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
