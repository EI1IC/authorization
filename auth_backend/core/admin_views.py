# core/admin_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Role, Resource, RolePermission, User, UserRole
from .auth import CustomJWTAuthentication
from .permissions import RBACPermission

class AdminRulesView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [RBACPermission]
    resource_name = "admin_rules"

    def get(self, request):
        data = []
        for role in Role.objects.all():
            perms = RolePermission.objects.filter(role=role).select_related("resource")
            data.append({
                "role": role.name,
                "permissions": [{"resource": p.resource.name, "action": p.action} for p in perms]
            })
        return Response(data)

    def post(self, request):
        role_name = request.data.get("role_name")
        resource_name = request.data.get("resource_name")
        action = request.data.get("action")
        if not all([role_name, resource_name, action]):
            return Response({"error": "role_name, resource_name, action обязательны"}, status=400)

        role, _ = Role.objects.get_or_create(name=role_name)
        resource, _ = Resource.objects.get_or_create(name=resource_name)
        _, created = RolePermission.objects.get_or_create(role=role, resource=resource, action=action)
        msg = "Создано" if created else "Уже существует"
        return Response({"message": msg}, status=201)

class AdminAssignRoleView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [RBACPermission]
    resource_name = "admin_rules"

    def post(self, request):
        email = request.data.get("email")
        role_name = request.data.get("role_name")
        try:
            user = User.objects.get(email=email)
            role = Role.objects.get(name=role_name)
            UserRole.objects.get_or_create(user=user, role=role)
            return Response({"message": f"Роль {role_name} назначена {email}"})
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)
        except Role.DoesNotExist:
            return Response({"error": "Роль не найдена"}, status=404)