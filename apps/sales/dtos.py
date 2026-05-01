from datetime import date
from decimal import Decimal
from typing import TypedDict


class CreateSaleDto(TypedDict):
    product_id: int
    quantity: int
    selling_price: Decimal
    date: date
    actor_id: int | None
    reference_id: str
