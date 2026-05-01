from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log, model_snapshot
from apps.finance.dtos import CreateDueTransactionDto
from apps.finance.models import DueTransaction


@transaction.atomic
def create_due(dto: CreateDueTransactionDto) -> DueTransaction:
    txn = DueTransaction.objects.create(
        type=dto["type"],
        amount=abs(dto["amount"]),
        date=dto["date"],
        reference=dto["reference"],
        note=dto["note"],
    )
    create_audit_log(
        action=AuditAction.CREATE,
        model_name="DueTransaction",
        object_id=str(txn.pk),
        actor_id=dto["actor_id"],
        before=None,
        after=model_snapshot(txn),
    )
    return txn


@transaction.atomic
def record_payment(dto: CreateDueTransactionDto) -> DueTransaction:
    payment_amount = abs(dto["amount"]) * Decimal("-1")
    txn = DueTransaction.objects.create(
        type=dto["type"],
        amount=payment_amount,
        date=dto["date"],
        reference=dto["reference"],
        note=dto["note"],
    )
    create_audit_log(
        action=AuditAction.CREATE,
        model_name="DueTransaction",
        object_id=str(txn.pk),
        actor_id=dto["actor_id"],
        before=None,
        after=model_snapshot(txn),
    )
    return txn
