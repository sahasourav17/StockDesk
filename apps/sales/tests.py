from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.products.models import Product
from apps.sales.services import create_sale
from apps.stock.models import StockTransaction, StockTransactionType
from apps.stock.services import create_stock_transaction
from apps.suppliers.models import Supplier


class SaleServiceTests(TestCase):
    def test_create_sale_creates_out_transaction(self) -> None:
        supplier = Supplier.objects.create(name="S1", contact_info="c", address="a")
        product = Product.objects.create(name="P1", supplier=supplier, selling_price=Decimal("10"))
        create_stock_transaction(
            {
                "product_id": product.id,
                "quantity_change": 10,
                "transaction_type": "IN",
                "supplier_price": Decimal("5"),
                "selling_price": None,
                "reference_id": "init",
                "actor_id": None,
            }
        )

        create_sale(
            {
                "product_id": product.id,
                "quantity": 3,
                "selling_price": Decimal("10"),
                "date": date.today(),
                "actor_id": None,
                "reference_id": "sale-1",
            }
        )

        out_exists = StockTransaction.objects.filter(
            product=product,
            transaction_type=StockTransactionType.OUT,
            quantity_change=-3,
        ).exists()
        self.assertTrue(out_exists)
