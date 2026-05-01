from django.db.models import Model
from django.http import HttpRequest

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log, model_snapshot


class AuditAdminMixin:
    audit_model_name: str | None = None

    def _model_name(self, obj: Model) -> str:
        return self.audit_model_name or obj.__class__.__name__

    def _actor_id(self, request: HttpRequest) -> int | None:
        return request.user.id if request.user.is_authenticated else None

    def audit_create(self, request: HttpRequest, obj: Model) -> None:
        create_audit_log(
            action=AuditAction.CREATE,
            model_name=self._model_name(obj),
            object_id=str(obj.pk),
            actor_id=self._actor_id(request),
            before=None,
            after=model_snapshot(obj),
        )

    def audit_update(self, request: HttpRequest, before: dict, obj: Model) -> None:
        create_audit_log(
            action=AuditAction.UPDATE,
            model_name=self._model_name(obj),
            object_id=str(obj.pk),
            actor_id=self._actor_id(request),
            before=before,
            after=model_snapshot(obj),
        )

    def audit_delete(self, request: HttpRequest, before: dict, obj: Model) -> None:
        create_audit_log(
            action=AuditAction.DELETE,
            model_name=self._model_name(obj),
            object_id=str(obj.pk),
            actor_id=self._actor_id(request),
            before=before,
            after=None,
        )
