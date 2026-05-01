from datetime import date
from decimal import Decimal
from typing import TypedDict


class CreateDueTransactionDto(TypedDict):
    type: str
    amount: Decimal
    date: date
    reference: str
    note: str
    actor_id: int | None
