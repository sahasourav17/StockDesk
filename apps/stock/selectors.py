from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.stock.models import StockTransaction


def get_product_stock(product_id: int) -> int:
    result = StockTransaction.objects.filter(product_id=product_id).aggregate(total=Coalesce(Sum("quantity_change"), 0))
    return int(result["total"])
