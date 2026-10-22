# Expense API

A small FastAPI application for recording expenses in SQLite.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```text

## Run

```bash
uvicorn  --reload
```text

The API is available at:

- API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

## Endpoints

### Create an expense

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "category": "food",
    "amount": 12.50,
    "description": "Lunch"
  }'
```text

### List expenses

```bash
curl http://127.0.0.1:8000/expenses
```text

### Set a monthly budget

Sets (creates or updates) a spending limit for a category in a given month. Posting again for the same `category` and `month` replaces the existing budget's amount rather than creating a duplicate.

Request body:

| Field          | Type   | Rules                                            |
|----------------|--------|---------------------------------------------------|
| `category`     | string | Must be one of the known categories (see below)   |
| `month`        | string | Must match `YYYY-MM` (e.g. `2024-05`)              |
| `limit_amount` | number | Must be greater than 0                            |

```bash
curl -X POST http://127.0.0.1:8000/budgets \
  -H "Content-Type: application/json" \
  -d '{
    "category": "food",
    "month": "2024-05",
    "limit_amount": 300.00
  }'
```text

Response (`200 OK`):

```json
{
  "id": 1,
  "category": "food",
  "month": "2024-05",
  "limit_amount": 300.0
}
```text

Invalid input (non-positive `limit_amount`, malformed `month`, or an unknown `category`) returns `422 Unprocessable Entity` with a validation error describing the problem.

### Get budget vs. actual spending for a month

Returns, for every category with a budget set in the requested month, the budget amount and the actual total spent on expenses in that category during that month. Categories with a budget but no matching expenses are included with `actual_spent: 0`.

```bash
curl http://127.0.0.1:8000/budgets/2024-05
```text

Response (`200 OK`):

```json
[
  {
    "category": "food",
    "month": "2024-05",
    "limit_amount": 300.0,
    "actual_spent": 180.0,
    "usage_ratio": 0.6
  }
]
```text

A `month` that does not match `YYYY-MM` returns `422 Unprocessable Entity`.

### Get budget alerts for a month

Returns only the categories that are approaching or over their budget for the requested month:

- **warning** — actual spending is at least 80% of the budget, but under 100%.
- **overspent** — actual spending is at or above 100% of the budget.

Categories under 80% usage, or with no budget set, do not appear in the response.

```bash
curl http://127.0.0.1:8000/alerts/2024-05
```text

Response (`200 OK`):

```json
[
  {
    "category": "food",
    "month": "2024-05",
    "limit_amount": 300.0,
    "actual_spent": 270.0,
    "usage_percentage": 90.0,
    "status": "warning"
  }
]
```text

A `month` that does not match `YYYY-MM` returns `422 Unprocessable Entity`.

## Test

```bash
pytest
```text
