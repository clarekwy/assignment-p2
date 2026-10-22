from app.models import Budget
from app.repositories import (
    create_budget,
    list_budgets_for_month,
    sum_expenses_by_category_for_month,
)
from app.schemas import BudgetCreate, BudgetStatus

WARNING_THRESHOLD = 0.80
OVERSPENT_THRESHOLD = 1.00


def set_monthly_budget(budget: BudgetCreate) -> Budget:
    return create_budget(budget)


def get_budget_status_for_month(month: str) -> list[BudgetStatus]:
    budgets = list_budgets_for_month(month)
    spend_by_category = sum_expenses_by_category_for_month(month)

    statuses: list[BudgetStatus] = []
    for budget in budgets:
        actual_spent = spend_by_category.get(budget.category, 0.0)
        usage_ratio = actual_spent / budget.limit_amount
        statuses.append(
            BudgetStatus(
                category=budget.category,
                month=budget.month,
                limit_amount=budget.limit_amount,
                actual_spent=actual_spent,
                usage_ratio=usage_ratio,
            )
        )

    return statuses


def get_categories_at_warning_threshold(month: str) -> list[BudgetStatus]:
    return [
        status
        for status in get_budget_status_for_month(month)
        if status.usage_ratio >= WARNING_THRESHOLD
    ]


def get_overspent_categories(month: str) -> list[BudgetStatus]:
    return [
        status
        for status in get_budget_status_for_month(month)
        if status.usage_ratio >= OVERSPENT_THRESHOLD
    ]
