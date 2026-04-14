# authorization
# Система аутентификации и авторизации (RBAC)

## Архитектура доступа
Используется Role-Based Access Control (RBAC) с явным маппингом `Ресурс × Действие`.
- `User` → имеет 1+ `Role` через `UserRole`
- `Role` → владеет набором `RolePermission`
- `RolePermission` → связывает `Resource` и `Action` (`read/create/update/delete`)
- Авторизация проверяет наличие записи в БД для текущего пользователя, ресурса и HTTP-метода.

## Аутентификация
- Кастомный JWT (HS256) через `PyJWT`
- Токен передаётся в заголовке `Authorization: Bearer <token>`
- Серверный logout реализован через таблицу `TokenBlacklist`
- Пароли хранятся через PBKDF2 (`make_password`)

## Безопасность
- Soft-delete (`is_active=False`) блокирует вход и авторизацию
- Токены имеют срок жизни 60 минут
- Валидация входных данных через DRF Serializers
- Разделение прав через кастомный `RBACPermission`

## Запуск
1. `python manage.py migrate`
2. `python manage.py seed_data`
3. `python manage.py runserver`
4. API доступно по `http://127.0.0.1:8000/api/`