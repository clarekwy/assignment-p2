from pathlib import Path

from fastapi.testclient import TestClient

from app import database as app_database
from app.database import get_connection
from app.main import app


def _client(tmp_path: Path, monkeypatch) -> TestClient:
    test_database = tmp_path / "test_budgets_summary_route.db"
    monkeypatch.setattr(app_database, "DATABASE_PATH", test_database)
    return TestClient(app)


def _seed_expense(category: str, amount: float, created_at: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO expenses (category, amount, description, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (category, amount, None, created_at),
        )


def test_get_budget_summary_returns_budget_and_actual_spending(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": 100.0},
        )
        _seed_expense("food", 40.0, "2024-05-10T12:00:00")
        _seed_expense("food", 20.0, "2024-05-20T12:00:00")

        response = client.get("/budgets/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "food"
    assert body[0]["month"] == "2024-05"
    assert body[0]["limit_amount"] == 100.0
    assert body[0]["actual_spent"] == 60.0


def test_budgeted_category_with_no_spending_returns_zero(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        client.post(
            "/budgets",
            json={"category": "travel", "month": "2024-05", "limit_amount": 50.0},
        )

        response = client.get("/budgets/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "travel"
    assert body[0]["actual_spent"] == 0.0


def test_expenses_from_different_month_are_excluded(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": 100.0},
        )
        _seed_expense("food", 40.0, "2024-05-10T12:00:00")
        _seed_expense("food", 999.0, "2024-06-01T12:00:00")

        response = client.get("/budgets/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["actual_spent"] == 40.0


def test_invalid_month_format_returns_422(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.get("/budgets/2024-13")

    assert response.status_code == 422
