from django.db import models

from apps.products.models import Product


class StockTransactionType(models.TextChoices):
    IN = "IN", "Stock In"
    OUT = "OUT", "Stock Out"
    DAMAGE = "DAMAGE", "Damage"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"


class StockTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_transactions")
    quantity_change = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=StockTransactionType.choices, db_index=True)
    supplier_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["product", "created_at"])]

    def __str__(self) -> str:
        return f"{self.product_id}:{self.transaction_type}:{self.quantity_change}"


class DamageRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="damage_records")
    quantity = models.PositiveIntegerField()
    date = models.DateField(db_index=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["product", "date"])]

    def __str__(self) -> str:
        return f"Damage #{self.pk}"
