from decimal import Decimal
from typing import Any

from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.finance.models import DueTransaction, DueType
from apps.products.models import Product
from apps.sales.models import Sale
from apps.stock.models import StockTransaction, StockTransactionType


def dashboard_callback(request: Any, context: dict[str, Any]) -> dict[str, Any]:
    today = timezone.localdate()

    total_sales = Sale.objects.filter(date=today).aggregate(total=Coalesce(Sum("total_price"), Decimal("0")))["total"]

    total_profit = StockTransaction.objects.filter(
        created_at__date=today,
        transaction_type=StockTransactionType.OUT,
    ).aggregate(
        total=Coalesce(
            Sum((F("selling_price") - F("supplier_price")) * -F("quantity_change")),
            Decimal("0"),
        )
    )["total"]

    due_totals = DueTransaction.objects.filter(date=today).aggregate(
        payable=Coalesce(Sum("amount", filter=Q(type=DueType.PAYABLE)), Decimal("0")),
        receivable=Coalesce(Sum("amount", filter=Q(type=DueType.RECEIVABLE)), Decimal("0")),
    )

    low_stock_count = (
        Product.objects.annotate(stock_qty=Coalesce(Sum("stock_transactions__quantity_change"), 0))
        .filter(stock_qty__lt=10)
        .count()
    )
    audit_logs = AuditLog.objects.select_related("user").order_by("-timestamp")[:10]

    context.update(
        {
            "dashboard_cards": [
                {
                    "title": "Total Sales (Today)",
                    "value": total_sales,
                    "link": reverse("admin:sales_sale_changelist"),
                },
                {
                    "title": "Total Profit (Today)",
                    "value": total_profit,
                    "link": reverse("admin:stock_stocktransaction_changelist"),
                },
                {
                    "title": "Total Payable (Today)",
                    "value": due_totals["payable"],
                    "link": reverse("admin:finance_duetransaction_changelist"),
                },
                {
                    "title": "Total Receivable (Today)",
                    "value": due_totals["receivable"],
                    "link": reverse("admin:finance_duetransaction_changelist"),
                },
                {
                    "title": "Low Stock Count (<10)",
                    "value": low_stock_count,
                    "link": f"{reverse('admin:products_product_changelist')}?low_stock=1",
                },
            ],
            "audit_logs": audit_logs,
            "today_sales_report_url": reverse("today-sales-report"),
        }
    )
    return context
