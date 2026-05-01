from datetime import UTC, datetime

from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.finance.models import DueTransaction
from apps.finance.services import create_due, record_payment


@admin.register(DueTransaction)
class DueTransactionAdmin(ModelAdmin):
    list_display = ("type", "amount", "date", "reference")
    list_filter = ("type", "date")
    search_fields = ("reference", "note")

    def save_model(self, request: HttpRequest, obj: DueTransaction, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return
        service = record_payment if obj.amount < 0 else create_due
        service(
            {
                "type": obj.type,
                "amount": obj.amount,
                "date": obj.date or datetime.now(UTC).date(),
                "reference": obj.reference,
                "note": obj.note,
                "actor_id": request.user.id if request.user.is_authenticated else None,
            }
        )
