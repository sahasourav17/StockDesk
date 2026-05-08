from django import forms
from django.contrib import admin, messages
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminIntegerFieldWidget

from apps.audit.admin_mixins import AuditAdminMixin
from apps.audit.services import model_snapshot
from apps.products.models import Product
from apps.stock.models import StockTransactionType
from apps.stock.services import create_stock_transaction


class LowStockFilter(admin.SimpleListFilter):
    title = "low stock"
    parameter_name = "low_stock"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> list[tuple[str, str]]:
        return [("1", "Low stock (<10)")]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Product]) -> QuerySet[Product]:
        if self.value() != "1":
            return queryset
        return queryset.annotate(
            stock_qty=Coalesce(Sum("stock_transactions__quantity_change"), 0)
        ).filter(stock_qty__lt=10)


class DeletedStatusFilter(admin.SimpleListFilter):
    title = "deleted status"
    parameter_name = "deleted"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> list[tuple[str, str]]:
        return [
            ("active", "Active"),
            ("deleted", "Deleted"),
            ("all", "All"),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Product]) -> QuerySet[Product]:
        value = self.value()
        if value == "deleted":
            return queryset.filter(is_deleted=True)
        if value == "all":
            return queryset
        return queryset.filter(is_deleted=False)


class ProductAdminForm(forms.ModelForm):
    opening_quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        required=False,
        help_text="Required while creating product; optional while editing",
        widget=UnfoldAdminIntegerFieldWidget(
            attrs={
                "min": 1,
                "step": 1,
                "inputmode": "numeric",
                "placeholder": "0",
            }
        ),
    )

    class Meta:
        model = Product
        fields = ("name", "supplier", "buying_price")

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean() or {}
        opening_quantity = cleaned_data.get("opening_quantity")
        if self.instance.pk is None and opening_quantity is None:
            raise forms.ValidationError("Quantity is required while creating a product.")
        return cleaned_data


@admin.register(Product)
class ProductAdmin(AuditAdminMixin, ModelAdmin):
    form = ProductAdminForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "supplier",
                    "buying_price",
                    "opening_quantity",
                ),
            },
        ),
    )
    list_display = ("name", "supplier", "buying_price", "current_stock", "is_deleted", "created_at", "actions_menu")
    search_fields = ("name",)
    list_filter = (DeletedStatusFilter, "supplier", "created_at", LowStockFilter)
    autocomplete_fields = ("supplier",)

    @admin.display(description="Actions")
    def actions_menu(self, obj: Product) -> str:
        delete_url = reverse("admin:products_product_delete", args=[obj.pk])
        return format_html(
            (
                '<a href="{}" class="rounded border border-red-500 px-2 py-1 '
                'text-xs font-medium text-red-600 hover:bg-red-50">Delete</a>'
            ),
            delete_url,
        )

    def save_model(self, request: HttpRequest, obj: Product, form: ModelForm, change: bool) -> None:
        opening_qty = int(form.cleaned_data.get("opening_quantity") or 0)
        before = model_snapshot(Product._base_manager.get(pk=obj.pk)) if change else None
        super().save_model(request, obj, form, change)
        if change and before is not None:
            self.audit_update(request, before, obj)
        elif not change:
            self.audit_create(request, obj)
        if opening_qty > 0:
            reference_prefix = "OPENING-STOCK" if not change else "ADDED-STOCK"
            create_stock_transaction(
                {
                    "product_id": obj.id,
                    "quantity_change": opening_qty,
                    "transaction_type": StockTransactionType.IN,
                    "supplier_price": obj.buying_price,
                    "selling_price": None,
                    "reference_id": f"{reference_prefix}-{obj.id}",
                    "actor_id": request.user.id if request.user.is_authenticated else None,
                }
            )
            self.message_user(request, f"{opening_qty} units added to stock.", level=messages.SUCCESS)

    def delete_model(self, request: HttpRequest, obj: Product) -> None:
        before = model_snapshot(obj)
        obj.delete()
        self.audit_delete(request, before, obj)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Product]) -> None:
        for obj in queryset:
            before = model_snapshot(obj)
            obj.delete()
            self.audit_delete(request, before, obj)

    def get_deleted_objects(
        self,
        objs: list[Product],
        request: HttpRequest,
    ) -> tuple[list[str], dict[str, int], set[str], list[str]]:
        # Soft delete does not remove related rows, so skip Django hard-delete cascade checks.
        return [str(obj) for obj in objs], {}, set(), []

    def get_queryset(self, request: HttpRequest) -> QuerySet[Product]:
        queryset = Product._base_manager.select_related("supplier")
        deleted = request.GET.get("deleted")
        if deleted == "all":
            return queryset
        if deleted == "deleted":
            return queryset.filter(is_deleted=True)
        return queryset.filter(is_deleted=False)
