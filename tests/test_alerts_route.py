from pathlib import Path

from fastapi.testclient import TestClient

from app import database as app_database
from app.database import get_connection
from app.main import app


def _client(tmp_path: Path, monkeypatch) -> TestClient:
    test_database = tmp_path / "test_alerts_route.db"
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


def _set_budget(client: TestClient, category: str, month: str, limit_amount: float) -> None:
    response = client.post(
        "/budgets",
        json={"category": category, "month": month, "limit_amount": limit_amount},
    )
    assert response.status_code == 200


def test_spending_below_80_percent_produces_no_alert(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        _set_budget(client, "food", "2024-05", 100.0)
        _seed_expense("food", 79.0, "2024-05-10T12:00:00")

        response = client.get("/alerts/2024-05")

    assert response.status_code == 200
    assert response.json() == []


def test_spending_exactly_at_80_percent_produces_warning(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        _set_budget(client, "food", "2024-05", 100.0)
        _seed_expense("food", 80.0, "2024-05-10T12:00:00")

        response = client.get("/alerts/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "food"
    assert body[0]["status"] == "warning"
    assert body[0]["usage_percentage"] == 80.0


def test_spending_between_80_and_100_percent_produces_warning(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        _set_budget(client, "food", "2024-05", 100.0)
        _seed_expense("food", 90.0, "2024-05-10T12:00:00")

        response = client.get("/alerts/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "warning"
    assert body[0]["usage_percentage"] == 90.0


def test_spending_exactly_at_100_percent_produces_overspent(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        _set_budget(client, "food", "2024-05", 100.0)
        _seed_expense("food", 100.0, "2024-05-10T12:00:00")

        response = client.get("/alerts/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "overspent"
    assert body[0]["usage_percentage"] == 100.0


def test_spending_above_100_percent_produces_overspent(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        _set_budget(client, "food", "2024-05", 100.0)
        _seed_expense("food", 150.0, "2024-05-10T12:00:00")

        response = client.get("/alerts/2024-05")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "overspent"
    assert body[0]["usage_percentage"] == 150.0


def test_invalid_month_format_returns_422(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.get("/alerts/2024-13")

    assert response.status_code == 422
