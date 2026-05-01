from datetime import date
from typing import TypedDict

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log, model_snapshot
from apps.products.models import Product
from apps.stock.models import DamageRecord
from apps.stock.services import create_stock_transaction


class CreateDamageDto(TypedDict):
    product_id: int
    quantity: int
    date: date
    note: str
    actor_id: int | None


@transaction.atomic
def create_damage(dto: CreateDamageDto) -> DamageRecord:
    product = Product.objects.select_for_update().get(pk=dto["product_id"])
    record = DamageRecord.objects.create(
        product=product,
        quantity=dto["quantity"],
        date=dto["date"],
        note=dto["note"],
    )
    create_stock_transaction(
        {
            "product_id": product.id,
            "quantity_change": -dto["quantity"],
            "transaction_type": "DAMAGE",
            "supplier_price": None,
            "selling_price": None,
            "reference_id": f"DAMAGE-{record.id}",
            "actor_id": dto["actor_id"],
        }
    )
    create_audit_log(
        action=AuditAction.CREATE,
        model_name="DamageRecord",
        object_id=str(record.pk),
        actor_id=dto["actor_id"],
        before=None,
        after=model_snapshot(record),
    )
    return record
