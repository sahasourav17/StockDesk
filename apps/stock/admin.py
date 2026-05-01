from datetime import UTC, datetime

from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.stock.damage_services import create_damage
from apps.stock.models import DamageRecord, StockTransaction
from apps.stock.services import create_stock_transaction


@admin.register(StockTransaction)
class StockTransactionAdmin(ModelAdmin):
    list_display = ("product", "quantity_change", "transaction_type", "supplier_price", "selling_price", "created_at")
    list_filter = ("transaction_type", "created_at", "product")
    search_fields = ("reference_id", "product__name")

    def save_model(self, request: HttpRequest, obj: StockTransaction, form: ModelForm, change: bool) -> None:
        if change:
            return
        create_stock_transaction(
            {
                "product_id": obj.product_id,
                "quantity_change": obj.quantity_change,
                "transaction_type": obj.transaction_type,
                "supplier_price": obj.supplier_price,
                "selling_price": obj.selling_price,
                "reference_id": obj.reference_id,
                "actor_id": request.user.id if request.user.is_authenticated else None,
            }
        )

    def has_change_permission(self, request: HttpRequest, obj: StockTransaction | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: StockTransaction | None = None) -> bool:
        return False


@admin.register(DamageRecord)
class DamageRecordAdmin(ModelAdmin):
    list_display = ("product", "quantity", "date", "note")
    list_filter = ("date", "product")
    search_fields = ("product__name", "note")

    def save_model(self, request: HttpRequest, obj: DamageRecord, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return
        create_damage(
            {
                "product_id": obj.product_id,
                "quantity": obj.quantity,
                "date": obj.date or datetime.now(UTC).date(),
                "note": obj.note,
                "actor_id": request.user.id if request.user.is_authenticated else None,
            }
        )
