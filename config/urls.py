from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from apps.reports.views import today_sales_report_csv

urlpatterns = [
    path("", lambda request: redirect("/admin/")),
    path("admin/reports/today-sales-report/", today_sales_report_csv, name="today-sales-report"),
    path("admin/", admin.site.urls),
]
