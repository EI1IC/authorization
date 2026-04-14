from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, TokenBlacklist
from .serializers import UserRegistrationSerializer, UserUpdateSerializer
from .jwt_utils import create_access_token, decode_access_token
from .auth import CustomJWTAuthentication
from .permissions import RBACPermission
import datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_data = create_access_token(user.id)
        return Response({"message": "Регистрация успешна", **token_data}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"error": "Email и пароль обязательны"}, status=400)
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({"error": "Неверные данные"}, status=401)

        if not user.check_password(password):
            return Response({"error": "Неверные данные"}, status=401)

        token_data = create_access_token(user.id)
        return Response({"message": "Успешный вход", **token_data})

class LogoutView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        payload = decode_access_token(token)
        TokenBlacklist.objects.create(token=token, expires_at=datetime.datetime.utcfromtimestamp(payload["exp"]))
        return Response({"message": "Выход выполнен"})

class ProfileView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserUpdateSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        request.user.is_active = False
        request.user.save()
        return Response({"message": "Аккаунт удалён (soft delete)"})

# Mock View для демонстрации RBAC
class PostMockView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [RBACPermission]
    resource_name = "posts"  # 🔑 Ключевой атрибут для авторизации

    def get(self, request):
        return Response({"data": ["post_1", "post_2", "post_3"]})

    def post(self, request):
        return Response({"message": "Пост создан"}, status=201)