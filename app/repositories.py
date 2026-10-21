from app.database import get_connection
from app.models import Expense
from app.schemas import ExpenseCreate


def create_expense(expense: ExpenseCreate) -> Expense:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses (category, amount, description)
            VALUES (?, ?, ?)
            """,
            (expense.category, expense.amount, expense.description),
        )

        row = connection.execute(
            """
            SELECT id, category, amount, description, created_at
            FROM expenses
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return Expense(**dict(row))


def list_expenses() -> list[Expense]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, category, amount, description, created_at
            FROM expenses
            ORDER BY id
            """
        ).fetchall()

    return [Expense(**dict(row)) for row in rows]
