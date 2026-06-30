# way_samurai

Страницы frontend (HTML, серверный рендеринг):

URL	Описание
/	Главная — плазменная live wallpaper + список статей
/login/	Вход
/register/	Регистрация
/logout/	Выход
/create/	Написать статью
/article/<id>/	Детальная страница статьи + комментарии
/edit/<id>/	Редактировать статью
/delete/<id>/	Удалить статью
/comment/<article_id>/	Создать комментарий
/comment/delete/<id>/	Удалить комментарий
Админка:

URL	Описание
/admin/	Django Admin (users, articles, comments, categories)
API (Django Ninja, JSON):

URL	Описание
/api/docs	Swagger UI документация (Django Ninja)
/api/openapi.json	OpenAPI схема
/api/users/register/	Регистрация
/api/users/login/	Вход (256-символьный токен)
/api/users/logout/	Выход
/api/users/me/	Текущий пользователь
/api/users/token/	Получить JWT
/api/users/token/refresh/	Обновить JWT
/api/token/pair	JWT pair (django-ninja-jwt)
/api/token/refresh	JWT refresh
/api/token/verify	JWT verify
/api/articles/	CRUD статей
/api/comments/	CRUD комментариев
/api/comments/by-article/<id>/	Комментарии статьи
/api/categories/	CRUD категорий

# 1. Запусти контейнеры
docker compose up --build

# 2. Открой в браузере:
http://localhost:8000/api/docs        # Swagger-документация (Django Ninja)
http://localhost:8000/admin/          # Админ-панель Django
Для админки сначала создай суперпользователя:
docker compose run --rm web python manage.py createsuperuser


Главная: http://localhost:8000/ 
Админка: http://localhost:8000/admin/ →  (login: admin / admin123)
Swagger docs at http://localhost:8000/api/docs
Внутри контейнера: python manage.py runserver на 0.0.0.0:8000
