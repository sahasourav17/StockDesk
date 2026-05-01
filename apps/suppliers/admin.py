from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.audit.admin_mixins import AuditAdminMixin
from apps.audit.services import model_snapshot
from apps.suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(AuditAdminMixin, ModelAdmin):
    list_display = ("name", "contact_info", "created_at", "updated_at", "actions_menu")
    search_fields = ("name", "contact_info", "address")
    list_filter = ("created_at", "updated_at")

    @admin.display(description="Actions")
    def actions_menu(self, obj: Supplier) -> str:
        delete_url = reverse("admin:suppliers_supplier_delete", args=[obj.pk])
        return format_html('<a href="{}" title="Delete" style="font-size:18px;">&#8942;</a>', delete_url)

    def save_model(self, request: HttpRequest, obj: Supplier, form: ModelForm, change: bool) -> None:
        before = model_snapshot(Supplier.objects.get(pk=obj.pk)) if change else None
        super().save_model(request, obj, form, change)
        if change and before is not None:
            self.audit_update(request, before, obj)
        elif not change:
            self.audit_create(request, obj)

    def delete_model(self, request: HttpRequest, obj: Supplier) -> None:
        before = model_snapshot(obj)
        super().delete_model(request, obj)
        self.audit_delete(request, before, obj)
