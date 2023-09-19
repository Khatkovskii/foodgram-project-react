![workflow](https://github.com/Khatkovskii/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Проект продуктовый помощник Foodgram

Foodgram - продуктовый помощник, позволяет публиковать рецепты,
подписываться на публикации других пользователей, добавлять понравившиеся
рецепты в «Избранное» и «Список покупок». Доступно скачивание 
списка продуктов в формате txt, необходимых для приготовления одного или
нескольких выбранных блюд.

Адрес сайта:
[foodhate.hopto.org](https://foodhate.hopto.org)  



## Описание проекта:
### Главная страница
На странице - cписок первых шести рецептов, отсортированных по дате публикации
(от новых к старым). Остальные рецепты доступны на следующих страницах: внизу
страницы есть пагинация.

### Страница рецепта
На странице - полное описание рецепта. Для авторизованных пользователей -
возможность добавить рецепт в избранное и в список покупок, возможность
подписаться на автора рецепта.

### Страница пользователя
На странице - имя пользователя, все рецепты, опубликованные пользователем и
возможность подписаться на пользователя.

### Подписка на авторов
Подписка на публикации доступна только авторизованному пользователю. Страница
подписок доступна только владельцу.


### Список избранного
Список избранного может просматривать только его владелец. Сценарий поведения пользователя:

### Список покупок
Список покупок может просматривать только его владелец.

Список покупок скачивается в формате txt. При скачивании списка покупок
ингредиенты в результирующем списке не дублируются;

### Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом.
Фильтрация может проводится по нескольким тегам. При фильтрации на странице
пользователя фильтруются только рецепты выбранного пользователя. Такой же
принцип соблюдается при фильтрации списка избранного.

## Workflow
Для использования Continuous Integration (CI) и Continuous Deployment (CD): в
репозитории GitHub Actions ```Settings/Secrets/Actions``` прописать Secrets -
переменные окружения для доступа к сервисам:

```
SECRET_KEY='<secret_key>'  # стандартный ключ, который создается при старте проекта,
                           # ключ должен быть заключен в '...'
DEBUG=False                # опция отладчика True/False
ALLOWED_HOSTS              # список хостов/доменов, для которых доступен текущий проект
                           # изменить IP-адрес сервера и/или добавить имя хоста

ENGINE=django.db.backends.postgresql
DB_NAME                    # имя БД - postgres (по умолчанию)
POSTGRES_USER              # логин для подключения к БД - postgres (по умолчанию)
POSTGRES_PASSWORD          # пароль для подключения к БД (установите свой)
DB_HOST=db                 # название сервиса (контейнера)
DB_PORT=5432               # порт для подключения к БД


DOCKER_USERNAME            # имя пользователя в DockerHub
DOCKER_PASSWORD            # пароль пользователя в DockerHub
HOST                       # ip_address сервера
USER                       # имя пользователя
SSH_KEY                    # приватный ssh-ключ локального ПК имеющего доступ к серверу (cat ~/.ssh/id_rsa)
                           # ключ вводится полностью, начиная с -----BEGIN OPENSSH PRIVATE KEY-----
                           # до -----END OPENSSH PRIVATE KEY-----

PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа

TELEGRAM_TO                # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN             # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

При push в ветку main автоматически отрабатывают сценарии:
* *tests* - проверка кода на соответствие стандарту PEP8.
Дальнейшие шаги выполняются только если push был в ветку main;
* *build_and_push_to_docker_hub* - сборка и доставка докер-образов на DockerHub
* *deploy* - автоматический деплой проекта на боевой сервер. Выполняется
копирование файлов из DockerHub на сервер;
* *send_message* - отправка уведомления в Telegram.


### Алгоритм регистрации пользователей
* Пользователь отправляет POST-запрос для регистрации нового пользователя 
на эндпойнт ```/api/users/```с параметрами:
```json
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```
* Пользователь отправляет POST-запрос на на эндпоинт ```/api/token/login/``` 
c данными указанными при регистрации:
```json
{
    "email": "vpupkin@yandex.ru",
    "password": "Qwerty123"
}
```
в ответе на запрос ему приходит:
```json
{
    "auth-token": "8c02a1..."
}
```

И далее тестируем API Foodgram согласно документации ```api/docs/redoc```.

## Автор бэкенда
[Хатковский Глеб](https://github.com/Khatkovskii)