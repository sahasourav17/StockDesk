from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log, model_snapshot
from apps.products.models import Product
from apps.sales.dtos import CreateSaleDto
from apps.sales.models import Sale
from apps.stock.models import StockTransactionType
from apps.stock.services import create_stock_transaction


@transaction.atomic
def create_sale(dto: CreateSaleDto) -> Sale:
    product = Product.objects.select_for_update().get(pk=dto["product_id"])
    latest_cost_transaction = product.stock_transactions.filter(quantity_change__gt=0).order_by("-created_at").first()
    supplier_price = latest_cost_transaction.supplier_price if latest_cost_transaction else Decimal("0")

    total_price = (dto["selling_price"] * Decimal(dto["quantity"])).quantize(Decimal("0.01"))
    sale = Sale.objects.create(
        product=product,
        quantity=dto["quantity"],
        selling_price=dto["selling_price"],
        total_price=total_price,
        date=dto["date"],
    )
    create_stock_transaction(
        {
            "product_id": product.id,
            "quantity_change": -dto["quantity"],
            "transaction_type": StockTransactionType.OUT,
            "supplier_price": supplier_price,
            "selling_price": dto["selling_price"],
            "reference_id": dto["reference_id"] or f"SALE-{sale.id}",
            "actor_id": dto["actor_id"],
        }
    )
    create_audit_log(
        action=AuditAction.CREATE,
        model_name="Sale",
        object_id=str(sale.pk),
        actor_id=dto["actor_id"],
        before=None,
        after=model_snapshot(sale),
    )
    return sale
