# Тестовое задание в компанию ВСпорте

## Запуск

Задайте следующие переменные окружения

для базы данных:
```ini
DB_HOST=localhost
DB_NAME=vsporte-auth-server
DB_PASS=P@ssw0rd
DB_PORT=5432
DB_USER=postgres
```

секретный ключ для генерации jwt токенов:
```ini
SECRET_KEY=myverysecretkey
```

Установите зависимости
```shell
pip install poetry
poetry install
```

Выполните миграцию:
```shell
alembic upgrade head
```

Запустите командой
```shell
uvicorn main:app --app-dir src/ 
```

### docker

Если у вас есть docker desktop, запустите приложение через файл `docker-compose.yml`. 
Миграция бд выполнится автоматически.
Создайте файл .env в корневой папке проекта. Заполните его переменными окружения.
Если база запущена локально и у вас windows, в переменную `DB_HOST` введите `host.docker.internal`.
На macOS/Linux воспользуйтесь network_mode: host или рекомендациями для своей операционной системы.
По умолчанию порт 8000.

## API

`post /jwt` получить jwt токен по паре (username или email) и password.
Токен выдаётся только для конкретного сервиса!
То есть, если администратор сервиса coolservice запросит jwt, то с ним он сможет выполнить операции только над пользователями coolservice.
Срок действия токена 1 день.

`get /users` Получить список всех пользователей (с пагинацией)

`post /users` Создать пользователя передав логин и пароль

`put /users/access` Добавить доступ для пользователя (роль в сервисе)

`delete /users` Удалить пользователя по логину

Страница `/docs` активна. В ней подписаны методы и возможные тела запросов. 
JWT токен можно подставить в блок Authorize, тогда авторизация будет выполняться автоматически при вызове методов.
Схема - Bearer.
Подставлять токен в чистом виде, без указания схемы.

Проект сделан с упором на безопасность (выдаются понятные сообщения об ошибках), а не на скорость (sql запросы могут быть более быстрыми)

## Начальные данные

Для удобства проверяющего на старте приложения создается пользователь:

username: vip

password: P@ssw0rd

email: user@mail.rb

role: admin

service: someservice

Если такой пользователь уже есть, то не создается
