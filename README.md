# Профильное задание: Python-разработчик
### Запуск сервиса:
* #### Выполнить `docker-compose up`
### Запуск тестов:
* #### Выполнить `docker-compose -f docker-compose.tests.yaml up`
## Краткая документация:
### 1) API
### Аутентификация по JWT
* /api/create-user - создать пользователя
* /api/token - получить access и refresh токены
* /api/token/refresh - обновить access и refresh токены
### Функционал сервиса:
* /api/friends/send-request - отправить запрос в друзья
* /api/friends/respond-to-request - принять/отклонить запрос в друзья
* /api/friends/revoke-request - Отозвать ранее отправленный запрос в друзья
* /api/friends/remove-friend - Удалить пользователя из друзей
* /api/friends/get-incoming-requests - Получить список людей, от которых есть входящий запрос в друзья
* /api/friends/get-outgoing-requests - Получить список людей, которым отправлен исходящий запрос в друзья
* /api/friends/get-friends - Получить список друзей
* /api/friends/get-status-with-user/{username} - Получить статус дружбы с пользователем {username}
#### Спецификация OpenAPI в файле `friedns_service.json`
### 2) Примеры вызова API:
* ### Регистрация:
  * Запрос:
  `curl -X POST --data "username=user1&password=123123" http://localhost:8000/api/create-user`
  * Ответ: `{"refresh":"{refresh_token}", "access":"{access_token}"}`
* ### Аутентификация:
  * Запрос: `curl -X POST --data "username=user1&password=123123" http://localhost:8000/api/token`
  * Ответ: `{"refresh":"{refresh_token}", "access":"{access_token}"}`
* ### Отправить запрос в друзья пользователю user2:
  * Запрос: `curl -X POST --header "Authorization: Bearer {access_token}" --data "username=user2" http://localhost:8000/api/friends/send-request`
* ### Принять запрос в друзья от пользователя user2:
  * Запрос: `curl -X POST --header "Authorization: Bearer {access_token}" --data "username=user2&action=true" http://localhost:8000/api/friends/respond-to-request`
* ### Получить список друзей
  * Запрос: `curl --header "Authorization: Bearer {access_token}" http://localhost:8000/api/friends/get-friends`
  * Ответ: `{"usernames":["name2","name3"]}`
* ### Удалить пользователя user2 из списка друзей
  * Запрос: `curl -X POST --header "Authorization: Bearer {access_token}" --data "username:user2" http://localhost:8000/api/friends/remove-friend`
### 3) Модели
### User: модель пользователя
* id: int 
* username: string
* password: string
### Relationship: модель отношения одного пользователя к другому
* id: int
* from_user: User
* to_user: User
* status: bool
##### Если status == False, значит есть запрос от from_user к to_user<br>Если status == True, значит from_user и to_user друзья
