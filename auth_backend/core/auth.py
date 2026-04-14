# core/auth.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_utils import decode_access_token
from .models import User, TokenBlacklist
import jwt

class CustomJWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        # 1. Извлекаем заголовок Authorization
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(self.keyword + " "):
            return None  # Нет токена → DRF продолжит поиск или вернёт 401

        token = auth_header.split(" ", 1)[1]

        # 2. Проверяем blacklist
        if TokenBlacklist.objects.filter(token=token).exists():
            raise AuthenticationFailed("Токен отозван (logout)")

        # 3. Декодируем
        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Токен истёк")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Невалидный токен")

        # 4. Ищем пользователя
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationFailed("Токен не содержит идентификатора")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed("Пользователь не найден или деактивирован")

        # 5. Возвращаем пару (user, token). DRF сохранит в request.user
        return (user, token)