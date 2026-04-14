# Система аутентификации и авторизации (RBAC)

Django-проект с кастомной JWT-аутентификацией и Role-Based Access Control (RBAC) для управления правами доступа.

## Описание

Проект реализует систему безопасности с явным маппингом `Ресурс × Действие`. Авторизация проверяет наличие записи в базе данных для текущего пользователя, ресурса и HTTP-метода.

### Основные возможности

- **Кастомная JWT-аутентификация** через библиотеку `PyJWT` (алгоритм HS256)
- **RBAC (Role-Based Access Control)** — гибкая система прав на основе ролей
- **Server-side logout** через таблицу чёрного списка токенов
- **Soft-delete** пользователей без физического удаления записей
- **Валидация данных** через DRF Serializers

## Архитектура доступа

```
User → UserRole → Role → RolePermission → Resource + Action
```

### Модели данных

| Модель | Описание |
|--------|----------|
| `User` | Кастомная модель пользователя (UUID, email, soft-delete) |
| `Role` | Роль (например: admin, viewer) |
| `Resource` | Бизнес-сущность (posts, reports, admin_rules) |
| `RolePermission` | Связка: Роль + Ресурс + Действие (read/create/update/delete) |
| `UserRole` | Привязка пользователя к ролям (многие-ко-многим) |
| `TokenBlacklist` | Отозванные JWT-токены для server-side logout |

## Аутентификация

- Токен передаётся в заголовке: `Authorization: Bearer <token>`
- Срок жизни токена: **60 минут**
- Пароли хранятся через **PBKDF2** (`make_password`)
- При logout токен добавляется в чёрный список

## Безопасность

- Soft-delete (`is_active=False`) блокирует вход и авторизацию
- Валидация входных данных через DRF Serializers
- Кастомный класс разрешений `RBACPermission`
- Проверка токена на отзыв при каждом запросе

## Быстрый старт

### Требования

- Python 3.12+
- PostgreSQL 12+
- Django 6.0+
- djangorestframework 3.14+
- PyJWT 2.8+
- psycopg2-binary 2.9+

### Установка

1. **Клонируйте репозиторий и перейдите в директорию проекта:**
   ```bash
   cd auth_backend
   ```

2. **Активируйте виртуальное окружение:**
   ```bash
   source venv/bin/activate  # Linux/macOS
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте базу данных PostgreSQL:**
   
   Убедитесь, что PostgreSQL запущен и создана БД `auth_db`:
   ```sql
   CREATE DATABASE auth_db;
   ```
   
   При необходимости измените параметры подключения в `config/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'auth_db',
           'USER': 'postgres',
           'PASSWORD': 'dev_pass_123',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Примените миграции:**
   ```bash
   python manage.py makemigrations core
   python manage.py migrate
   ```

6. **Заполните БД тестовыми данными:**
   ```bash
   python manage.py seed_data
   ```

7. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver
   ```

8. **API доступно по адресу:** `http://127.0.0.1:8000/api/`

## API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register/` | Регистрация нового пользователя |
| POST | `/api/auth/login/` | Вход (получение JWT-токена) |
| POST | `/api/auth/logout/` | Выход (добавление токена в blacklist) |
| GET | `/api/auth/profile/` | Получение профиля текущего пользователя |
| PATCH | `/api/auth/profile/` | Обновление профиля |
| DELETE | `/api/auth/profile/` | Удаление аккаунта (soft delete) |

### Бизнес-логика (демо RBAC)

| Метод | Endpoint | Описание | Требуемое право |
|-------|----------|----------|-----------------|
| GET | `/api/mock/posts/` | Список постов | `posts.read` |
| POST | `/api/mock/posts/` | Создание поста | `posts.create` |

### Администрирование

| Метод | Endpoint | Описание | Требуемое право |
|-------|----------|----------|-----------------|
| GET | `/api/admin/rules/` | Просмотр всех правил RBAC | `admin_rules.read` |
| POST | `/api/admin/rules/` | Создание нового правила | `admin_rules.create` |
| POST | `/api/admin/assign-role/` | Назначение роли пользователю | `admin_rules.create` |

## Примеры запросов

### Регистрация пользователя

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }'
```

### Вход

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123"
  }'
```

**Ответ:**
```json
{
  "message": "Успешный вход",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### Запрос с токеном

```bash
curl -X GET http://127.0.0.1:8000/api/mock/posts/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Назначение роли

```bash
curl -X POST http://127.0.0.1:8000/api/admin/assign-role/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role_name": "admin"
  }'
```

### Создание правила доступа

```bash
curl -X POST http://127.0.0.1:8000/api/admin/rules/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "manager",
    "resource_name": "reports",
    "action": "delete"
  }'
```

## Тестовые учётные данные

После выполнения `seed_data` доступны следующие пользователи:

| Email | Пароль | Роль | Права |
|-------|--------|------|-------|
| `admin@test.com` | `admin123` | admin | Полный доступ ко всем ресурсам |
| `viewer@test.com` | `viewer123` | viewer | Только чтение `posts` и `reports` |

## Структура проекта

```
auth_backend/
├── config/                 # Настройки Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Конфигурация проекта
│   ├── urls.py             # Корневые URL
│   └── wsgi.py
├── core/                   # Основное приложение
│   ├── __init__.py
│   ├── models.py           # Модели данных (User, Role, Resource...)
│   ├── views.py            # API Views
│   ├── admin_views.py      # Админские Views
│   ├── serializers.py      # DRF Serializers
│   ├── permissions.py      # RBACPermission класс
│   ├── auth.py             # CustomJWTAuthentication
│   ├── jwt_utils.py        # Утилиты для работы с JWT
│   ├── urls.py             # Маршруты API
│   ├── tests.py            # Тесты
│   └── management/
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── seed_data.py  # Команда заполнения тестовыми данными
├── requirements.txt        # Зависимости Python
├── manage.py               # Django CLI утилита
├── README.md               # Этот файл
└── venv/                   # Виртуальное окружение (не коммитить)
```

## Лицензия
Программ создана в образовательных целях для выполнения тестового задания
