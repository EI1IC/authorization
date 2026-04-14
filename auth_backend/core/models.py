# core/models.py
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
import uuid

# 1. Менеджер пользователей (отвечает за создание users)
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Хеширует пароль через PBKDF2
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# 2. Кастомная модель пользователя
class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)  # Soft-delete
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "email"  # Поле для логина
    REQUIRED_FIELDS = []      # Поля, запрашиваемые при createsuperuser

    def __str__(self):
        return self.email

# 3. Роли
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

# 4. Ресурсы (бизнес-сущности)
class Resource(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Например: posts, reports, admin_rules")

# 5. Права (связка Роль + Ресурс + Действие)
class RolePermission(models.Model):
    ACTION_CHOICES = [("read", "Чтение"), ("create", "Создание"), ("update", "Изменение"), ("delete", "Удаление")]
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)

    class Meta:
        unique_together = ("role", "resource", "action")  # Защита от дублей

# 6. Привязка пользователя к ролям
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

# 7. Чёрный список токенов (для server-side logout)
class TokenBlacklist(models.Model):
    token = models.CharField(max_length=500, unique=True)
    expires_at = models.DateTimeField()