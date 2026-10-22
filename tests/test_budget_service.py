from pathlib import Path

import app.database
from app.database import get_connection, initialize_database
from app.schemas import BudgetCreate
from app.services import (
    get_budget_status_for_month,
    get_categories_at_warning_threshold,
    get_overspent_categories,
    set_monthly_budget,
)


def _seed_expense(category: str, amount: float, created_at: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO expenses (category, amount, description, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (category, amount, None, created_at),
        )


def _use_test_database(tmp_path: Path, monkeypatch) -> None:
    test_database = tmp_path / "test_budget_service.db"
    monkeypatch.setattr(app.database, "DATABASE_PATH", test_database)
    initialize_database()


def test_set_monthly_budget_persists_budget(tmp_path: Path, monkeypatch) -> None:
    _use_test_database(tmp_path, monkeypatch)

    budget = set_monthly_budget(
        BudgetCreate(category="food", month="2024-05", limit_amount=100.0)
    )

    assert budget.id == 1
    assert budget.category == "food"
    assert budget.month == "2024-05"
    assert budget.limit_amount == 100.0


def test_get_budget_status_for_month_computes_actual_spent_and_ratio(
    tmp_path: Path, monkeypatch
) -> None:
    _use_test_database(tmp_path, monkeypatch)

    set_monthly_budget(BudgetCreate(category="food", month="2024-05", limit_amount=100.0))
    _seed_expense("food", 40.0, "2024-05-10T12:00:00")
    _seed_expense("food", 20.0, "2024-05-20T12:00:00")
    _seed_expense("food", 999.0, "2024-06-01T12:00:00")  # different month, excluded

    statuses = get_budget_status_for_month("2024-05")

    assert len(statuses) == 1
    assert statuses[0].category == "food"
    assert statuses[0].actual_spent == 60.0
    assert statuses[0].usage_ratio == 0.6


def test_budgeted_category_with_no_expenses_has_zero_spend(
    tmp_path: Path, monkeypatch
) -> None:
    _use_test_database(tmp_path, monkeypatch)

    set_monthly_budget(BudgetCreate(category="travel", month="2024-05", limit_amount=50.0))

    statuses = get_budget_status_for_month("2024-05")

    assert len(statuses) == 1
    assert statuses[0].actual_spent == 0.0
    assert statuses[0].usage_ratio == 0.0


def test_category_at_warning_threshold_is_included(tmp_path: Path, monkeypatch) -> None:
    _use_test_database(tmp_path, monkeypatch)

    set_monthly_budget(BudgetCreate(category="food", month="2024-05", limit_amount=100.0))
    _seed_expense("food", 80.0, "2024-05-10T12:00:00")

    warnings = get_categories_at_warning_threshold("2024-05")

    assert len(warnings) == 1
    assert warnings[0].category == "food"
    assert warnings[0].usage_ratio == 0.8


def test_category_below_warning_threshold_is_excluded(tmp_path: Path, monkeypatch) -> None:
    _use_test_database(tmp_path, monkeypatch)

    set_monthly_budget(BudgetCreate(category="food", month="2024-05", limit_amount=100.0))
    _seed_expense("food", 79.0, "2024-05-10T12:00:00")

    warnings = get_categories_at_warning_threshold("2024-05")

    assert warnings == []


def test_category_at_or_over_overspent_threshold_is_included(
    tmp_path: Path, monkeypatch
) -> None:
    _use_test_database(tmp_path, monkeypatch)

    set_monthly_budget(BudgetCreate(category="food", month="2024-05", limit_amount=100.0))
    _seed_expense("food", 100.0, "2024-05-10T12:00:00")

    overspent = get_overspent_categories("2024-05")

    assert len(overspent) == 1
    assert overspent[0].category == "food"
    assert overspent[0].usage_ratio == 1.0


def test_category_under_overspent_threshold_is_excluded_but_still_warned(
    tmp_path: Path, monkeypatch
) -> None:
    _use_test_database(tmp_path, monkeypatch)

    set_monthly_budget(BudgetCreate(category="food", month="2024-05", limit_amount=100.0))
    _seed_expense("food", 90.0, "2024-05-10T12:00:00")

    overspent = get_overspent_categories("2024-05")
    warnings = get_categories_at_warning_threshold("2024-05")

    assert overspent == []
    assert len(warnings) == 1
    assert warnings[0].usage_ratio == 0.9
