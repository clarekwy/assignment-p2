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


def create_budget(budget: BudgetCreate) -> Budget:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO budgets (category, month, limit_amount)
            VALUES (?, ?, ?)
            """,
            (budget.category, budget.month, budget.limit_amount),
        )

        row = connection.execute(
            """
            SELECT id, category, month, limit_amount
            FROM budgets
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return Budget(**dict(row))


def list_budgets() -> list[Budget]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, category, month, limit_amount
            FROM budgets
            ORDER BY id
            """
        ).fetchall()

    return [Budget(**dict(row)) for row in rows]


def upsert_budget(budget: BudgetCreate) -> Budget:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO budgets (category, month, limit_amount)
            VALUES (?, ?, ?)
            ON CONFLICT (category, month) DO UPDATE SET limit_amount = excluded.limit_amount
            """,
            (budget.category, budget.month, budget.limit_amount),
        )

        row = connection.execute(
            """
            SELECT id, category, month, limit_amount
            FROM budgets
            WHERE category = ? AND month = ?
            """,
            (budget.category, budget.month),
        ).fetchone()

    return Budget(**dict(row))


def list_budgets_for_month(month: str) -> list[Budget]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, category, month, limit_amount
            FROM budgets
            WHERE month = ?
            ORDER BY category
            """,
            (month,),
        ).fetchall()

    return [Budget(**dict(row)) for row in rows]


def sum_expenses_by_category_for_month(month: str) -> dict[str, float]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE strftime('%Y-%m', created_at) = ?
            GROUP BY category
            """,
            (month,),
        ).fetchall()

    return {row["category"]: row["total"] for row in rows}