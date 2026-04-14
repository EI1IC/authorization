# core/jwt_utils.py
import jwt
import datetime
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: str) -> dict:
    """Создаёт JWT и возвращает словарь с токеном и TTL."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),                 # subject: ID пользователя
        "iat": now,                          # issued at: время выдачи
        "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # expiry
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

def decode_access_token(token: str) -> dict:
    """Декодирует и проверяет JWT. Бросает исключения при ошибках."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])