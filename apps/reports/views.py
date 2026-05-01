import csv
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from apps.sales.models import Sale


@staff_member_required
def today_sales_report_csv(request: HttpRequest) -> HttpResponse:
    today = timezone.localdate()
    sales = Sale.objects.filter(date=today).select_related("product").order_by("id")
    total_sales = sales.aggregate(total=Coalesce(Sum("total_price"), Decimal("0")))["total"]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="today-sales-{today}.csv"'

    writer = csv.writer(response)
    writer.writerow(["date", "product", "quantity", "selling_price", "total_price"])
    for sale in sales:
        writer.writerow([sale.date, sale.product.name, sale.quantity, sale.selling_price, sale.total_price])

    writer.writerow([])
    writer.writerow(["total_sales", total_sales])
    return response
