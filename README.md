# bot_for_scheduling
## Телеграмм бот для планирования v1.0
Бот создан для ведения какого-либо расписания (например для школьного)
по принципу "Предмет: Задачи"<br>
Пользователю предлагается создать один предмет (например, "Домашние дела") и в рамках него создавать тематические задачи,
(например "Покормить кота").<br>
Каждая задача имеет название и опциональные параметры: дедлайн, описание и напоминания 

### Используемый стек
* **Python 3.11**
* **Aiogram 3.x.x** (основной фреймворк)
* **APScheduler** для работы напоминаний
* **MongoDB** как основная БД
* **Redis** как БД для машины состояний
* **Docker и Docker Compose** для быстрого развертывания

### Баги v1.0 (когда-нибудь исправлю)
* Если задача имеет несколько напоминаний с одинаковым временем, 
то при удалении одного из них удаляются все с аналогичным временем
Можно пофиксить каким-нибудь словарем где key-value будет uuid: datetime
* Очевидный (раньше был неочевидный :( ) баг, когда у пользователя несколько предметов с одинаковым названием
Следствием является то, что  все задачи из этих предметов смешиваются в кучу, 
поэтому работа с одним предметом отражается на другом (+ удаление одного удаляет и копии). 
Фиксится каким нибудь uuid при создании задания и помещения этого uuid в subject
* пользователь может выбрать напоминание, которое должно было случиться в прошлом 
(например если сейчас 12:00 и дедлайн 12:30, то пользователь может выбрать напоминание "за 1 час", 
т.е которое должно было быть в 11:30) - создается неработающее напоминание