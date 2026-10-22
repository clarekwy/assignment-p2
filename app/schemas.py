import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ExpenseCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=500)


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    amount: float
    description: str | None
    created_at: datetime


class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    month: str
    limit_amount: float = Field(gt=0)

    @field_validator("month")
    @classmethod
    def validate_month_format(cls, value: str) -> str:
        if not MONTH_PATTERN.match(value):
            raise ValueError("month must be in YYYY-MM format")
        return value


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    month: str
    limit_amount: float


    class BudgetStatus(BaseModel):
    category: str
    month: str
    limit_amount: float
    actual_spent: float
    usage_ratio: float