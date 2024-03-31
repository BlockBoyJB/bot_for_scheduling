# bot_for_scheduling
## Телеграмм бот для планирования v2.0
Бот создан для ведения какого-либо расписания
по принципу "Раздел: Задачи"<br>
Пользователю предлагается создать один раздел (например, "Домашние дела") и в рамках него создавать тематические задачи,
(например "Покормить кота").<br>
Каждая задача имеет название и опциональные параметры: дедлайн, описание и напоминания.<br>
В версии 2.0 появилась возможность добавлять собственные сообщения к напоминанию

### Используемый стек
* **Python 3.11**
* **Aiogram 3.x.x** (основной фреймворк)
* **APScheduler** для работы напоминаний
* **PostgreSQL** как основная БД
* **Redis** как БД для машины состояний
* **Docker и Docker Compose** для быстрого развертывания

### Баги v2.0 (когда-нибудь исправлю)
* (баг с v1.0) пользователь может выбрать напоминание, которое должно было случиться в прошлом
(например если сейчас 12:00 и дедлайн 12:30, то пользователь может выбрать напоминание "за 1 час", 
т.е которое должно было быть в 11:30) - создается неработающее напоминание