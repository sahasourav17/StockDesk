from django.db import models


class DueType(models.TextChoices):
    PAYABLE = "PAYABLE", "Payable"
    RECEIVABLE = "RECEIVABLE", "Receivable"


class DueTransaction(models.Model):
    type = models.CharField(max_length=20, choices=DueType.choices, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(db_index=True)
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["type", "date"])]

    def __str__(self) -> str:
        return f"{self.type} {self.amount}"
