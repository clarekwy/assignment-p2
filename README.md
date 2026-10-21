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

## Test

```bash
pytest
```text
