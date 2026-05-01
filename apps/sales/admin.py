from datetime import UTC, datetime
from typing import Any

from django import forms
from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.products.models import Product
from apps.sales.models import Sale
from apps.sales.services import create_sale
from apps.stock.selectors import get_product_stock
from apps.stock.services import InsufficientStockError


class SaleAdminForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ("product", "quantity", "selling_price", "date")

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean() or {}
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")
        if not isinstance(product, Product) or not isinstance(quantity, int):
            return cleaned_data
        available_stock = get_product_stock(product.id)
        if quantity > available_stock:
            raise forms.ValidationError(
                f"Insufficient stock. Available stock for {product.name}: {available_stock}."
            )
        return cleaned_data


@admin.register(Sale)
class SaleAdmin(ModelAdmin):
    form = SaleAdminForm
    list_display = ("product", "quantity", "selling_price", "total_price", "date")
    list_filter = ("date", "product")
    search_fields = ("product__name",)

    def save_model(self, request: HttpRequest, obj: Sale, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return
        try:
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
        except InsufficientStockError as exc:
            self.message_user(request, str(exc), level=messages.ERROR)
