from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.audit.admin_mixins import AuditAdminMixin
from apps.audit.services import model_snapshot
from apps.suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(AuditAdminMixin, ModelAdmin):
    list_display = ("name", "contact_info", "created_at", "updated_at")
    search_fields = ("name", "contact_info", "address")
    list_filter = ("created_at", "updated_at")

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
