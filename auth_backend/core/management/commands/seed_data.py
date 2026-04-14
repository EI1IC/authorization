from django.core.management.base import BaseCommand
from core.models import User, Role, Resource, RolePermission, UserRole
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными"

    def handle(self, *args, **kwargs):
        # Пользователи
        admin = User.objects.create(email="admin@test.com", password=make_password("admin123"), first_name="Админ")
        viewer = User.objects.create(email="viewer@test.com", password=make_password("viewer123"), first_name="Зритель")

        # Роли
        r_admin, _ = Role.objects.get_or_create(name="admin", defaults={"description": "Полный доступ"})
        r_viewer, _ = Role.objects.get_or_create(name="viewer", defaults={"description": "Только чтение"})

        # Ресурсы
        res_posts, _ = Resource.objects.get_or_create(name="posts")
        res_reports, _ = Resource.objects.get_or_create(name="reports")
        res_rules, _ = Resource.objects.get_or_create(name="admin_rules")

        # Права
        for action in ["read", "create", "update", "delete"]:
            RolePermission.objects.get_or_create(role=r_admin, resource=res_posts, action=action)
            RolePermission.objects.get_or_create(role=r_admin, resource=res_reports, action=action)
            RolePermission.objects.get_or_create(role=r_admin, resource=res_rules, action=action)

        RolePermission.objects.get_or_create(role=r_viewer, resource=res_posts, action="read")
        RolePermission.objects.get_or_create(role=r_viewer, resource=res_reports, action="read")

        # Назначение
        UserRole.objects.get_or_create(user=admin, role=r_admin)
        UserRole.objects.get_or_create(user=viewer, role=r_viewer)

        self.stdout.write(self.style.SUCCESS("Тестовые данные загружены"))