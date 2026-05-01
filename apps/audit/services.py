from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db.models import Model

from apps.audit.models import AuditAction, AuditLog

User = get_user_model()


def _normalize(value: Any) -> Any:
    if isinstance(value, Model):
        return value.pk
    if isinstance(value, (datetime, date, Decimal, UUID)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(v) for v in value]
    return value


def create_audit_log(
    *,
    action: AuditAction,
    model_name: str,
    object_id: str,
    actor_id: int | None,
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
) -> AuditLog:
    payload = {
        "before": _normalize(dict(before or {})),
        "after": _normalize(dict(after or {})),
    }
    user = User.objects.filter(id=actor_id).first() if actor_id is not None else None
    return AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        changes=payload,
    )


def model_snapshot(instance: Model) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for field in instance._meta.fields:
        data[field.name] = _normalize(getattr(instance, field.name))
    return data
