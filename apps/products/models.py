from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.suppliers.models import Supplier


class ProductQuerySet(models.QuerySet["Product"]):
    def delete(self) -> tuple[int, dict[str, int]]:
        updated = super().update(is_deleted=True, deleted_at=timezone.now())
        return updated, {self.model._meta.label: updated}


class ProductManager(models.Manager["Product"]):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db).filter(is_deleted=False)


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="products")
    buying_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        indexes = [models.Index(fields=["supplier", "name"])]

    def __str__(self) -> str:
        return self.name

    @property
    def current_stock(self) -> int:
        result = self.stock_transactions.aggregate(total=Coalesce(Sum("quantity_change"), 0))
        return int(result["total"])

    @property
    def estimated_unit_profit(self) -> Decimal:
        latest_in = self.stock_transactions.filter(quantity_change__gt=0).order_by("-created_at").first()
        if self.buying_price is None or latest_in is None or latest_in.supplier_price is None:
            return Decimal("0")
        return self.buying_price - latest_in.supplier_price

    def delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        if self.is_deleted:
            return 0, {}
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return 1, {self._meta.label: 1}
