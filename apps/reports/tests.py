from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.products.models import Product
from apps.reports.selectors import get_date_range_profit
from apps.sales.services import create_sale
from apps.stock.services import create_stock_transaction
from apps.suppliers.models import Supplier


class ReportSelectorTests(TestCase):
    def test_profit_calculation_for_date_range(self) -> None:
        supplier = Supplier.objects.create(name="S1", contact_info="c", address="a")
        product = Product.objects.create(name="P1", supplier=supplier, buying_price=Decimal("10"))

        create_stock_transaction(
            {
                "product_id": product.id,
                "quantity_change": 5,
                "transaction_type": "IN",
                "supplier_price": Decimal("6"),
                "selling_price": None,
                "reference_id": "in-1",
                "actor_id": None,
            }
        )
        create_sale(
            {
                "product_id": product.id,
                "quantity": 5,
                "selling_price": Decimal("10"),
                "date": date.today(),
                "actor_id": None,
                "reference_id": "sale-1",
            }
        )
        report = get_date_range_profit(date.today(), date.today())
        self.assertEqual(report["total_revenue"], Decimal("50"))
        self.assertEqual(report["total_cost"], Decimal("30"))
        self.assertEqual(report["total_profit"], Decimal("20"))
