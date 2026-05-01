from decimal import Decimal

from django.test import TestCase

from apps.products.models import Product
from apps.stock.services import InsufficientStockError, create_stock_transaction
from apps.suppliers.models import Supplier


class StockServiceTests(TestCase):
    def test_prevent_negative_stock(self) -> None:
        supplier = Supplier.objects.create(name="S1", contact_info="c", address="a")
        product = Product.objects.create(name="P1", supplier=supplier, buying_price=Decimal("10"))

        with self.assertRaises(InsufficientStockError):
            create_stock_transaction(
                {
                    "product_id": product.id,
                    "quantity_change": -1,
                    "transaction_type": "OUT",
                    "supplier_price": None,
                    "selling_price": Decimal("10"),
                    "reference_id": "o1",
                    "actor_id": None,
                }
            )
