from typing import Any, cast

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpRequest

from apps.users.models import User, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "role", "is_active")
    list_filter = ("role", "is_active", "is_superuser")
    fieldsets = cast(Any, DjangoUserAdmin.fieldsets) + ((None, {"fields": ("role",)}),)
    add_fieldsets = cast(Any, DjangoUserAdmin.add_fieldsets) + ((None, {"fields": ("role",)}),)

    def has_module_permission(self, request: HttpRequest) -> bool:
        return bool(request.user.is_authenticated and request.user.role == UserRole.SUPER_ADMIN)

    def has_view_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        return self.has_module_permission(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return self.has_module_permission(request)

    def has_change_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        return self.has_module_permission(request)

    def has_delete_permission(self, request: HttpRequest, obj: User | None = None) -> bool:
        return self.has_module_permission(request)
