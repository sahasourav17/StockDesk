from django.db import models
from django.utils import timezone


class SupplierQuerySet(models.QuerySet["Supplier"]):
    def delete(self) -> tuple[int, dict[str, int]]:
        updated = super().update(is_deleted=True, deleted_at=timezone.now())
        return updated, {self.model._meta.label: updated}


class SupplierManager(models.Manager["Supplier"]):
    def get_queryset(self) -> SupplierQuerySet:
        return SupplierQuerySet(self.model, using=self._db).filter(is_deleted=False)


class Supplier(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    contact_info = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SupplierManager()

    def __str__(self) -> str:
        return self.name

    def delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        if self.is_deleted:
            return 0, {}
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return 1, {self._meta.label: 1}
