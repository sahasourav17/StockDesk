from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    contact_info = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
