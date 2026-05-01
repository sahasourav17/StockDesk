from datetime import UTC, datetime

from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.sales.models import Sale
from apps.sales.services import create_sale


@admin.register(Sale)
class SaleAdmin(ModelAdmin):
    list_display = ("product", "quantity", "selling_price", "total_price", "date")
    list_filter = ("date", "product")
    search_fields = ("product__name",)

    def save_model(self, request: HttpRequest, obj: Sale, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return
        create_sale(
            {
                "product_id": obj.product_id,
                "quantity": obj.quantity,
                "selling_price": obj.selling_price,
                "date": obj.date or datetime.now(UTC).date(),
                "actor_id": request.user.id if request.user.is_authenticated else None,
                "reference_id": f"SALE-ADMIN-{obj.product_id}",
            }
        )
