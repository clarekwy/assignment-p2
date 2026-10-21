from pathlib import Path

from fastapi.testclient import TestClient

from app import database as app_database
from app.main import app


def test_create_expense_uses_sqlite(tmp_path: Path, monkeypatch) -> None:
    test_database = tmp_path / "test_expenses.db"
    monkeypatch.setattr(app_database, "DATABASE_PATH", test_database)

    with TestClient(app) as client:
        response = client.post(
            "/expenses",
            json={
                "category": "food",
                "amount": 12.50,
                "description": "Lunch",
            },
        )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["category"] == "food"
    assert response.json()["amount"] == 12.50
    assert response.json()["description"] == "Lunch"


def test_get_expenses_returns_saved_expenses(tmp_path: Path, monkeypatch) -> None:
    test_database = tmp_path / "test_expenses.db"
    monkeypatch.setattr(app_database, "DATABASE_PATH", test_database)

    with TestClient(app) as client:
        client.post(
            "/expenses",
            json={"category": "transport", "amount": 25, "description": "Train"},
        )
        client.post(
            "/expenses",
            json={"category": "food", "amount": 8.75, "description": "Coffee"},
        )

        response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["category"] == "transport"
    assert response.json()[1]["category"] == "food"


def test_create_expense_rejects_non_positive_amount() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/expenses",
            json={"category": "food", "amount": 0},
        )

    assert response.status_code == 422
    assert "greater than 0" in response.text
