from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.audit.admin_mixins import AuditAdminMixin
from apps.audit.services import model_snapshot
from apps.suppliers.models import Supplier


class DeletedStatusFilter(admin.SimpleListFilter):
    title = "deleted status"
    parameter_name = "deleted"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> list[tuple[str, str]]:
        return [
            ("active", "Active"),
            ("deleted", "Deleted"),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Supplier]) -> QuerySet[Supplier]:
        value = self.value()
        if value == "deleted":
            return queryset.filter(is_deleted=True)
        if value == "all":
            return queryset
        return queryset.filter(is_deleted=False)


@admin.register(Supplier)
class SupplierAdmin(AuditAdminMixin, ModelAdmin):
    list_display = ("name", "contact_info", "is_deleted", "created_at", "updated_at", "actions_menu")
    search_fields = ("name", "contact_info", "address")
    list_filter = (DeletedStatusFilter, "created_at", "updated_at")

    @admin.display(description="Actions")
    def actions_menu(self, obj: Supplier) -> str:
        if obj.is_deleted:
            restore_url = reverse("admin:suppliers_supplier_restore", args=[obj.pk])
            return format_html(
                (
                    '<a href="{}" class="rounded border border-green-500 px-2 py-1 '
                    'text-xs font-medium text-green-700 hover:bg-green-50">Undo Delete</a>'
                ),
                restore_url,
            )

        delete_url = reverse("admin:suppliers_supplier_delete", args=[obj.pk])
        return format_html(
            (
                '<a href="{}" class="rounded border border-red-500 px-2 py-1 '
                'text-xs font-medium text-red-600 hover:bg-red-50">Delete</a>'
            ),
            delete_url,
        )

    def save_model(self, request: HttpRequest, obj: Supplier, form: ModelForm, change: bool) -> None:
        before = model_snapshot(Supplier._base_manager.get(pk=obj.pk)) if change else None
        super().save_model(request, obj, form, change)
        if change and before is not None:
            self.audit_update(request, before, obj)
        elif not change:
            self.audit_create(request, obj)

    def delete_model(self, request: HttpRequest, obj: Supplier) -> None:
        before = model_snapshot(obj)
        obj.delete()
        self.audit_delete(request, before, obj)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Supplier]) -> None:
        for obj in queryset:
            before = model_snapshot(obj)
            obj.delete()
            self.audit_delete(request, before, obj)

    def get_deleted_objects(
        self,
        objs: list[Supplier],
        request: HttpRequest,
    ) -> tuple[list[str], dict[str, int], set[str], list[str]]:
        # Soft delete does not remove related rows, so skip Django hard-delete cascade checks.
        return [str(obj) for obj in objs], {}, set(), []

    def get_queryset(self, request: HttpRequest) -> QuerySet[Supplier]:
        queryset = Supplier._base_manager.all()
        deleted = request.GET.get("deleted")
        if deleted is None:
            return queryset
        if deleted == "deleted":
            return queryset.filter(is_deleted=True)
        if deleted == "active":
            return queryset.filter(is_deleted=False)
        return queryset

    def get_urls(self) -> list:
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/restore/",
                self.admin_site.admin_view(self.restore_view),
                name="suppliers_supplier_restore",
            ),
        ]
        return custom_urls + urls

    def restore_view(self, request: HttpRequest, object_id: str) -> HttpResponseRedirect:
        obj = Supplier._base_manager.filter(pk=object_id).first()
        if obj is None:
            self.message_user(request, "Supplier not found.", level=messages.ERROR)
            return HttpResponseRedirect(reverse("admin:suppliers_supplier_changelist"))
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj.is_deleted:
            before = model_snapshot(obj)
            obj.is_deleted = False
            obj.deleted_at = None
            obj.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
            self.audit_update(request, before, obj)
            self.message_user(request, f"Restored supplier: {obj.name}", level=messages.SUCCESS)
        else:
            self.message_user(request, "Supplier is already active.", level=messages.WARNING)

        return HttpResponseRedirect(reverse("admin:suppliers_supplier_changelist"))
