# Foodgram

### Cписок используемых технологий:
<div align="center">
	<img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" alt="Python" title="Python"/>
	<img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/django/django-plain.svg" alt="Django" title="Django"/>
  <img width="50" src="https://s3.amazonaws.com/media-p.slid.es/uploads/708405/images/4005243/django_rest_500x500.png" alt="DjangoRestFramework" title="DjangoRestFramework"/>
  <img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/githubactions/githubactions-original.svg" alt="Githubactions" title="Githubactions"/>
	<img width="50" src="https://user-images.githubusercontent.com/25181517/192109061-e138ca71-337c-4019-8d42-4792fdaa7128.png" alt="Postman" title="Postman"/>
  <img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-plain-wordmark.svg" alt="Postgresql" title="Postgresql"/>
  <img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/nginx/nginx-original.svg" alt="Nginx" title="Nginx"/>
</div>
          

Foodgram — это веб-приложение, где пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на других авторов. Зарегистрированные пользователи также могут создавать «Список покупок», который поможет собрать все нужные продукты для приготовления выбранных блюд.

___

### _Развернуть проект на удаленном сервере:_

**_Клонировать репозиторий:_**
```
git@github.com:ClinkyClink/foodgram.git
```
**_Установить на сервере Docker, Docker Compose:_**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
**_Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):_**
```
scp docker-compose.yml nginx.conf username@IP:/home/username/

# username - имя пользователя на сервере
# IP - публичный IP сервера

**_Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**_
```
sudo docker compose up -d
```
**_Выполнить миграции:_**
```
sudo docker compose exec backend python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
**_Наполнить базу данных содержимым из файла ingredients.json:_**
```
sudo docker compose exec backend python manage.py loaddata ingredients.json
```
**_Создать суперпользователя:_**
```
sudo docker compose exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```
### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram о успешном, либо завершившемся с ошибкой деплое

```

### Набор доступных эндпоинтов:

- ```api/tags/``` - Получение, списка тегов (GET).
- ```api/ingredients/``` - Получение, списка ингредиентов (GET).
- ```api/ingredients/``` - Получение ингредиента с соответствующим id (GET).
- ```api/tags/{id}``` - Получение, тега с соответствующим id (GET).
- ```api/recipes/``` - Получение списка с рецептами и публикация рецептов (GET, POST).
- ```api/recipes/{id}``` - Получение, изменение, удаление рецепта с соответствующим id (GET, PUT, PATCH, DELETE).
- ```api/recipes/{id}/shopping_cart/``` - Добавление рецепта с соответствующим id в список покупок и удаление из списка (GET, DELETE).
- ```api/recipes/download_shopping_cart/``` - Скачать файл со списком покупок TXT (в дальнейшем появиться поддержка PDF) (GET).
- ```api/recipes/{id}/favorite/``` - Добавление рецепта с соответствующим id в список избранного и его удаление (GET, DELETE).

#### Операции с пользователями:
- ```api/users/``` - получение информации о пользователе и регистрация новых пользователей. (GET, POST).
- ```api/users/{id}/``` - Получение информации о пользователе. (GET).
- ```api/users/me/``` - получение и изменение данных своей учётной записи. Доступна любым авторизованными пользователям (GET).
- ```api/users/set_password/``` - изменение собственного пароля (PATCH).
- ```api/users/{id}/subscribe/``` - Подписаться на пользователя с соответствующим id или отписаться от него. (GET, DELETE).
- ```api/users/subscribe/subscriptions/``` - Просмотр пользователей на которых подписан текущий пользователь. (GET).


## Автор:
• [Евгений](https://github.com/ClinkyClink)
