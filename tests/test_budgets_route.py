from pathlib import Path

from fastapi.testclient import TestClient

from app import database as app_database
from app.main import app


def _client(tmp_path: Path, monkeypatch) -> TestClient:
    test_database = tmp_path / "test_budgets_route.db"
    monkeypatch.setattr(app_database, "DATABASE_PATH", test_database)
    return TestClient(app)


def test_create_budget_succeeds(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": 100.0},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "food"
    assert body["month"] == "2024-05"
    assert body["limit_amount"] == 100.0


def test_setting_budget_again_for_same_category_and_month_replaces_it(
    tmp_path: Path, monkeypatch
) -> None:
    with _client(tmp_path, monkeypatch) as client:
        first = client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": 100.0},
        )
        second = client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": 150.0},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["limit_amount"] == 150.0


def test_zero_amount_is_rejected(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": 0},
        )

    assert response.status_code == 422
    assert "greater than 0" in response.text


def test_negative_amount_is_rejected(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.post(
            "/budgets",
            json={"category": "food", "month": "2024-05", "limit_amount": -10},
        )

    assert response.status_code == 422
    assert "greater than 0" in response.text


def test_invalid_month_format_is_rejected(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.post(
            "/budgets",
            json={"category": "food", "month": "2024-13", "limit_amount": 100.0},
        )

    assert response.status_code == 422
    assert "YYYY-MM" in response.text


def test_unknown_category_is_rejected(tmp_path: Path, monkeypatch) -> None:
    with _client(tmp_path, monkeypatch) as client:
        response = client.post(
            "/budgets",
            json={"category": "not-a-real-category", "month": "2024-05", "limit_amount": 100.0},
        )

    assert response.status_code == 422
    assert "category must be one of" in response.text
