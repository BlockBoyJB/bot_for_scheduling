# bot_for_scheduling

## Телеграмм бот для планирования v2.1

Бот создан для ведения какого-либо расписания
по принципу "Раздел: Задачи"<br>
Пользователю предлагается создать один раздел (например, "Домашние дела") и в рамках него создавать тематические задачи,
(например "Покормить кота").<br>
Каждая задача имеет название и опциональные параметры: дедлайн, описание и напоминания.<br>
В версии 2.0 появилась возможность добавлять собственные сообщения к напоминанию<br>
В версии 2.1 появилась возможность добавлять свой собственный часовой пояс (чтобы указывать время в своем часовом поясе
а не переводить каждый раз)

### Используемый стек

* **Python 3.11**
* **Aiogram 3.x.x** (основной фреймворк)
* **APScheduler** для работы напоминаний
* **PostgreSQL** как основная БД
* **Redis** как БД для машины состояний
* **Docker и Docker Compose** для быстрого развертывания

#### In new versions:
* Улучшение, оптимизация кода
* Исправление незначительных багов
* Тестирование
* И многое другое... (я не придумал что)