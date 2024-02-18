from datetime import datetime


class CmdText:
    start = (
        "Приветствуем в нашем телеграмм боте для трекинга заданий!\n"
        "Создать новый предмет: /create\n"
        "Перейти в главное меню: /menu\n"
        "Помощь: /help"
    )

    menu = (
        "Вы находитесь в главном меню.\n"
        "Вы можете перейти к:\n"
        "Предметам: /subjects\n"
        "Просмотреть все созданные задания: /hometasks\n"
        "Создать новый предмет: /create\n"
        "Помощь: /help"
    )

    help = (
        "Помощь\n"
        "Этот бот создан для ведения расписания (например школьного).\n"
        'Работает по принципу "предмет -> задачи"\n'
        "Существуют следущие команды:\n"
        "/subjects - посмотреть все предметы, которые вы создали\n"
        "/create - создать новый предмет\n"
        "/menu - главное меню\n"
        "/hometasks - посмотреть все задачи, которые вы создали (по всем предметам)\n"
    )

    default = "К предметам: /subjects\nВ главное меню: /menu"


class SubjectText:
    create = (
        "Вы находитесь в меню создания нового предмета.\n"
        "Пожалуйста, напишите без ошибок название для предмета:"
    )
    subject_created = (
        "Вы указали: {subject}\n"
        "Новый предмет успешно создан\n\n"
        "Перейти к предметам: /subjects\n"
        "В главное меню: /menu\n"
        "Создать еще один предмет: /create"
    )
    subject = (
        "Вы находитесь в меню выбора предмета.\n"
        "Пожалуйста, выберите один из предметов и нажмите на кнопку:"
    )
    no_subjects = (
        "Ой! Кажется у Вас нет ни одного предмета!\nСоздать новый предмет: /create"
    )
    subject_choose = (
        "Вы выбрали предмет: {subject}\n" "Выберите дальшейшие действия с предметом:"
    )
    wrong_subject_choose = (
        "Извините, но такого предмета у вас нет!\nПожалуйста, выберите из списка ниже:"
    )
    new_name = "Введите новое название для предмета (желательно короткое)"
    new_name_changed = "Имя предмета успешно изменено на {new_name}\n" + CmdText.default
    confirm_delete = (
        "Внимание! Вы собираетесь удалить предмет!\n"
        "Данное действие будет невозможно отменить\n"
        "Удаление предмета приведет к потере всех задач, записанных в этот предмет\n"
        "Вы точно хотите удалить предмет?"
    )
    delete_subject = "Предмет {subject} был успешно удален!\n" + CmdText.default
    no_delete_subject = "Предмет не был удален!\n" + CmdText.default


class HometaskText:
    hometask = (
        "Название: {title}:\n\t\t"
        "Дедлайн: {deadline}\n\t\t"
        "Описание: {description}\n\t\t"
        "Напоминания: {notifications}\n\t\t"
        "Дата создания: {create_date}"
    )
    no_all_hometasks = "Кажется, у Вас нет ни одного записанного задания!"
    no_hometasks = (
        'Ой! Кажется никаких задач по предмету "{subject}" нет!\n'
        "Хотите создать новое задание?\n"
        'Нажмите кнопку "Создать новую задачу"'
    )
    enter_title = "Пожалуйста, введите название для нового дз (рекомендуем короткое для удобства):"
    enter_deadline = (
        "Пожалуйста, укажите дедлайн (дату и время) задания\n"
        "Рекомендуется писать в обычном формате,\n"
        "Hапример 23 01 24, 12:00\n"
        "Либо нажмите любую из кнопок."
    )
    set_custom_deadline = (
        "Введите свое значение для напоминания\nОбязательно в минутах!"
    )
    incorrect_custom_deadline = (
        "Ой! Кажется, вы неправильно ввели время для напоминания!\n"
        + set_custom_deadline
    )
    incorrect_deadline = (
        "Ой! Кажется вы ввели некорректный формат для времени!\n"
        "Пожалуйста, введите дедлайн в формате\n"
        "ДАТА МЕСЯЦ ГОД, для времени (если необходимо): ЧАС:МИНУТА"
    )
    enter_description = (
        "Пожалуйста, укажите описание к задаче (одним сообщением до 1024х символов)"
    )
    add_notification = "Хотите добавить напоминание?"
    create_hometask = (
        "Отлично! Вы создали новое задание по предмету {subject}\n"
        "Название для задания: {title}\n"
        "Дедлайн задания: {deadline}\n"
        "Описание к задаче: {description}\n"
    )
    incorrect_number = (
        "Ой! Кажется вы выбрали номер, которого нет в списке!\n"
        "Пожалуйста, повторите выбор"
    )
    update_title = (
        'Название для задачи "{title}" успешно изменено на "{new_title}"\n'
        + CmdText.default
    )
    update_description = (
        "Описание для задачи {title} успешно обновлено!\n" + CmdText.default
    )
    update_deadline = "Дедлайн задачи успешно изменен на {deadline}\n" + CmdText.default
    deadline_with_notifications = (
        "Вы успешно изменили дедлайн задачи на {deadline}.\n"
        "Однако, у данной задачи были созданы напоминания\n"
        "({notifications})\n"
        "Вы можете выбрать новое время или оставить старое"
    )
    success_delete_hometask = "Задача {title} успешно удалена!\n" + CmdText.default
    no_delete_hometask = "Задача не была удалена!\n" + CmdText.default

    @classmethod
    async def format_notifications(
        cls, deadline: datetime, notifications: list[datetime]
    ) -> str:
        if len(notifications) == 0:
            return "без напоминаний"
        text = ""
        for notification in notifications:
            text += (
                f"за {round((deadline - notification).total_seconds() // 60)} минут, "
            )
        return text[:-2]

    @classmethod
    async def format_task(cls, task: dict):
        """
        task:
            _id: Object
            user_id: int
            subject: str
            title: str
            deadline: datetime
            description: str
            notifications: [datetime]
            scheduler_id: [str-uuid]
            create_date: datetime
        """
        return cls.hometask.format(
            title=task["title"],
            deadline=task["deadline"] if task["deadline"] else "без дедлайна",
            description=task["description"],
            notifications=await cls.format_notifications(
                task["deadline"], task["notifications"]
            ),
            create_date=task["create_date"],
        )

    @classmethod
    async def format_all_tasks(cls, hometasks: list[dict]) -> str:
        text = "Вот все задания, которые записаны у Вас:\n"
        for task in hometasks:
            text += (
                f"Предмет {task['subject']}\n\t"
                + cls.hometask.format(
                    title=task["title"],
                    deadline=task["deadline"] if task["deadline"] else "без дедлайна",
                    description=task["description"],
                    notifications=await cls.format_notifications(
                        task["deadline"], task["notifications"]
                    ),
                    create_date=task["create_date"],
                )
                + "\n\n"
            )
        return text

    @classmethod
    async def format_all_subject_tasks(
        cls, hometasks: list[dict]
    ) -> tuple[int, str, dict]:
        """
        hometasks = [{
            _id: Object,
            user_id: int,
            subject: str,
            title: str,
            deadline: datetime,
            description: str,
            notifications: [datetime],
            scheduler_id: [str-uuid],
            create_date: datetime
            }, {}]
        """
        k = 0
        text = ""
        state_data = {}
        for task in hometasks:
            k += 1
            text += (
                f"{k}. "
                + cls.hometask.format(
                    title=task["title"],
                    deadline=task["deadline"] if task["deadline"] else "без дедлайна",
                    description=task["description"],
                    notifications=await cls.format_notifications(
                        task["deadline"], task["notifications"]
                    ),
                    create_date=task["create_date"],
                )
                + "\n\n"
            )
            state_data[str(k)] = task["title"]
        return k, text, state_data


class NotificationText:
    set_notification = "Отлично! Теперь выберите за сколько минут до указанного времени напомнить Вам о задаче"
    set_custom_notificaion = "Пожалуйста, укажите свое время (В минутах!) за сколько нужно отправить уведомление"
    save_notifications = (
        "Все напоминания были сохранены и обновлены в соответствии с новым дедлайном\n"
        + CmdText.default
    )
    update_notification = "Время напоминания успешно обновлено\n" + CmdText.default
    delete_many_notifications = "Все напоминания были удалены\n" + CmdText.default
    delete_notification = "Напоминание успешно удалено\n" + CmdText.default
    created_notification = "Напоминание успешно создано!\n" + CmdText.default
    new_notification = "Добавлено новое напоминание {notification}\n" + CmdText.default
    further_actions = (
        "Что будем делать дальше?\n"
        "В главное меню: /menu\n"
        "Создать еще один предмет: /create\n"
        "Перейти к предметам: /subjects\n"
        "Посмотреть все задания: /homeworks\n"
        "Либо нажмите на кнопку, чтобы создать еще одно задание"
    )
    incorrect_notification_btn = (
        "Пожалуйста, выбирайте только из доступных ниже кнопок!"
    )
    choose_update_action = "Выберите действие с напоминанием:"
    new_time_notification = (
        "Пожалуйста, выберите новое время, за сколько напомнить о задаче.\n"
        "Либо Вы можете написать свое время (обязательно в минутах!)"
    )
    notification = "За {notification} минут.\n\t\tКогда (точное время): {time}"

    @classmethod
    async def format_notification(
        cls, deadline: datetime, scheduler_id: list[str], notifications: list[datetime]
    ) -> tuple[int, dict[str, str], str]:
        state_data = {}
        text = ""
        k = 0
        for i in range(len(notifications)):
            k += 1
            minutes = (deadline - notifications[i]).total_seconds()
            text += (
                f"{k}. "
                + cls.notification.format(
                    notification=round(minutes // 60), time=notifications[i]
                )
                + "\n\n"
            )
            state_data[str(k)] = scheduler_id[i]
        return k, state_data, text


class Buttons:
    subject_actions = [
        "Посмотреть все задачи",
        "Редактировать название",
        "Создать новую задачу",
        "Удалить предмет",
    ]

    hometask_action = [
        "Изменить название",
        "Редактировать описание",
        "Изменить дедлайн",
        "Удалить задачу",
        # "Редактировать напоминание",
        # "Добавить напоминание",
    ]
    enter_deadline = [
        "Через 5 минут",
        "Через 10 минут",
        "Через 15 минут",
        "Через 30 минут",
        "Через 1 час",
        "Свое время",
        "Без дедлайна",
    ]
    set_notification = [
        "За 5 минут",
        "За 10 минут",
        "За 15 минут",
        "За 30 минут",
        "За 1 час",
        "Свое время",
    ]
    notification_actions = ["Изменить время напоминания", "Удалить напоминание"]
