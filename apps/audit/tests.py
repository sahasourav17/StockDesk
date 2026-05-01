from decimal import Decimal

from django.test import TestCase

from apps.audit.models import AuditLog
from apps.products.models import Product
from apps.stock.services import create_stock_transaction
from apps.suppliers.models import Supplier


class AuditLogTests(TestCase):
    def test_stock_transaction_creates_audit_log(self) -> None:
        supplier = Supplier.objects.create(name="S1", contact_info="c", address="a")
        product = Product.objects.create(name="P1", supplier=supplier, selling_price=Decimal("10"))

        create_stock_transaction(
            {
                "product_id": product.id,
                "quantity_change": 2,
                "transaction_type": "IN",
                "supplier_price": Decimal("5"),
                "selling_price": None,
                "reference_id": "in1",
                "actor_id": None,
            }
        )

        self.assertEqual(AuditLog.objects.filter(model_name="StockTransaction").count(), 1)
