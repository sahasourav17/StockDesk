from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.suppliers.models import Supplier


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="products")
    buying_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        if latest_in is None or latest_in.supplier_price is None:
            return Decimal("0")
        return self.buying_price - latest_in.supplier_price
