from dataclasses import dataclass
from datetime import datetime


@dataclass
class Expense:
    id: int
    category: str
    amount: float
    description: str | None
    created_at: datetime


@dataclass
class Budget:
    id: int
    category: str
    month: str
    limit_amount: float