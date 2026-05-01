from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.audit.admin_mixins import AuditAdminMixin
from apps.audit.services import model_snapshot
from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(AuditAdminMixin, ModelAdmin):
    list_display = ("name", "supplier", "selling_price", "current_stock", "created_at")
    search_fields = ("name",)
    list_filter = ("supplier", "created_at")
    autocomplete_fields = ("supplier",)

    def save_model(self, request: HttpRequest, obj: Product, form: ModelForm, change: bool) -> None:
        before = model_snapshot(Product.objects.get(pk=obj.pk)) if change else None
        super().save_model(request, obj, form, change)
        if change and before is not None:
            self.audit_update(request, before, obj)
        elif not change:
            self.audit_create(request, obj)

    def delete_model(self, request: HttpRequest, obj: Product) -> None:
        before = model_snapshot(obj)
        super().delete_model(request, obj)
        self.audit_delete(request, before, obj)
