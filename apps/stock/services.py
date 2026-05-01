from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log, model_snapshot
from apps.products.models import Product
from apps.stock.dtos import CreateStockTransactionDto
from apps.stock.models import StockTransaction


class InsufficientStockError(ValueError):
    pass


@transaction.atomic
def create_stock_transaction(dto: CreateStockTransactionDto) -> StockTransaction:
    product = Product.objects.select_for_update().get(pk=dto["product_id"])
    current_stock = (
        StockTransaction.objects.select_for_update()
        .filter(product_id=product.id)
        .aggregate(total=Coalesce(Sum("quantity_change"), 0))["total"]
    )
    new_stock = int(current_stock) + dto["quantity_change"]
    if new_stock < 0:
        raise InsufficientStockError("Cannot create transaction that would result in negative stock")

    stock_txn = StockTransaction.objects.create(
        product=product,
        quantity_change=dto["quantity_change"],
        transaction_type=dto["transaction_type"],
        supplier_price=dto["supplier_price"],
        selling_price=dto["selling_price"],
        reference_id=dto["reference_id"],
    )
    create_audit_log(
        action=AuditAction.CREATE,
        model_name="StockTransaction",
        object_id=str(stock_txn.pk),
        actor_id=dto["actor_id"],
        before=None,
        after=model_snapshot(stock_txn),
    )
    return stock_txn
