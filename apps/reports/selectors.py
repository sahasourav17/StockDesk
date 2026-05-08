from datetime import date
from decimal import Decimal

from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from apps.sales.models import Sale
from apps.stock.models import StockTransaction, StockTransactionType


def get_daily_report(report_date: date) -> dict[str, Decimal | int]:
    stock_in = int(
        StockTransaction.objects.filter(
            created_at__date=report_date,
            transaction_type=StockTransactionType.IN,
        ).aggregate(total=Coalesce(Sum("quantity_change"), 0))["total"]
    )

    stock_out = int(
        abs(
            StockTransaction.objects.filter(
                created_at__date=report_date,
                transaction_type__in=[StockTransactionType.OUT, StockTransactionType.DAMAGE],
            ).aggregate(total=Coalesce(Sum("quantity_change"), 0))["total"]
        )
    )

    total_sales = Sale.objects.filter(date=report_date).aggregate(total=Coalesce(Sum("total_price"), Decimal("0")))[
        "total"
    ]

    damage_count = StockTransaction.objects.filter(
        created_at__date=report_date,
        transaction_type=StockTransactionType.DAMAGE,
    ).count()

    profit = StockTransaction.objects.filter(
        created_at__date=report_date,
        transaction_type=StockTransactionType.OUT,
    ).aggregate(
        total=Coalesce(
            Sum((F("selling_price") - F("supplier_price")) * -F("quantity_change")),
            Decimal("0"),
        )
    )["total"]

    return {
        "total_stock_in": stock_in,
        "total_stock_out": stock_out,
        "total_sales": total_sales,
        "damage_count": damage_count,
        "profit": profit,
    }


def get_date_range_profit(start_date: date, end_date: date) -> dict[str, Decimal]:
    in_cost = StockTransaction.objects.filter(
        created_at__date__range=(start_date, end_date),
        transaction_type=StockTransactionType.IN,
    ).aggregate(total=Coalesce(Sum(F("supplier_price") * F("quantity_change")), Decimal("0")))["total"]

    revenue = Sale.objects.filter(date__range=(start_date, end_date)).aggregate(
        total=Coalesce(Sum("total_price"), Decimal("0"))
    )["total"]

    return {
        "total_revenue": revenue,
        "total_cost": in_cost,
        "total_profit": revenue - in_cost,
    }


def get_sales_summary(start_date: date, end_date: date) -> dict[str, Decimal | int]:
    total_sales = Sale.objects.filter(date__range=(start_date, end_date)).aggregate(
        total=Coalesce(Sum("total_price"), Decimal("0")),
        total_qty=Coalesce(Sum("quantity"), 0),
    )
    total_profit = StockTransaction.objects.filter(
        created_at__date__range=(start_date, end_date),
        transaction_type=StockTransactionType.OUT,
    ).aggregate(
        total=Coalesce(
            Sum((F("selling_price") - F("supplier_price")) * -F("quantity_change")),
            Decimal("0"),
        )
    )["total"]

    return {
        "total_sales_amount": total_sales["total"],
        "total_profit": total_profit,
        "total_sold_quantity": int(total_sales["total_qty"]),
    }
