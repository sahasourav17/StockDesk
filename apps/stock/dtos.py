from decimal import Decimal
from typing import TypedDict


class CreateStockTransactionDto(TypedDict):
    product_id: int
    quantity_change: int
    transaction_type: str
    supplier_price: Decimal | None
    selling_price: Decimal | None
    reference_id: str
    actor_id: int | None
