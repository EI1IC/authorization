# core/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import RolePermission

class RBACPermission(BasePermission):
    """Проверяет права по схеме: Роль → Ресурс → Действие."""
    method_to_action = {
        "GET": "read", "POST": "create",
        "PUT": "update", "PATCH": "update", "DELETE": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False  # DRF сам вернёт 401 через AuthenticationFailed

        action = self.method_to_action.get(request.method)
        if not action:
            return True  # Неизвестный метод → разрешаем

        # Ресурс берём из атрибута view (указывается в каждом классе)
        resource_name = getattr(view, "resource_name", None)
        if not resource_name:
            return True  # Если ресурс не указан, пропускаем

        # Проверяем наличие права в БД одним запросом
        has_access = RolePermission.objects.filter(
            role__userrole__user=user,
            resource__name=resource_name,
            action=action
        ).exists()

        if not has_access:
            raise PermissionDenied("Доступ запрещён")
        return True