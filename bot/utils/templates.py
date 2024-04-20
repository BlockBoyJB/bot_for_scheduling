from bot.db import NotificationModel, TaskModel


class CmdText:
    start = (
        "Приветствуем в нашем телеграмм боте для отслеживания задач!\n"
        "Создать новый раздел с задачами: /new_section\n"
        "Перейти в главное меню: /menu\n"
        "Помощь: /help"
    )

    menu = (
        "Вы находитесь в главном меню.\n"
        "Вы можете перейти к:\n"
        "Разделам: /sections\n"
        "Просмотреть все созданные задания: /tasks\n"
        "Создать новый раздел: /new_section\n"
        "Помощь: /help"
    )
    help = (
        "Помощь\n"
        "Этот бот создан для отслеживания задач.\n"
        'Работает по принципу "предмет(тема) -> задачи",\n'
        "то есть вы можете создавать определенные разделы и внутри них создавать тематические задачки.\n"
        'Например: создаем раздел "Домашние дела" и внутри него создаем задачу "Покормить кота".\n'
        "Существуют следущие команды:\n"
        "/sections - посмотреть все разделы, которые вы создали\n"
        "/new_section - создать новый раздел\n"
        "/menu - главное меню\n"
        "/tasks - посмотреть все задачи, которые вы создали (по всем разделам)\n"
    )

    default = "К разделам: /sections\nВ главное меню: /menu"

    incorrect_btn = "Пожалуйста, выбирайте только из доступных ниже кнопок!"


class SectionText:
    create = (
        "Вы находитесь в меню создания нового раздела.\n"
        "Пожалуйста, введите без ошибок название для нового раздела:"
    )
    create_success = (
        "Вы указали {section}\n"
        "Новый раздел успешно создан\n"
        "Перейти к разделам: /sections\n"
        "В главное меню: /menu\n"
        "Создать еще один раздел: /new_section"
    )
    choose_section = (
        "Вы находитесь в меню выбора раздела.\n"
        "Выберите один из разделов и нажмите на кнопку:"
    )
    no_sections = (
        "Ой! Кажется, у вас нет ни одного созданного раздела!\n"
        "Создать новый раздел: /new_section"
    )
    chosen_section = "Вы выбрали секцию: {section}\nВыберите дальнейшие действия:"

    edit_name = "Имя раздела успешно изменено на {new_name}\n" + CmdText.default
    confirm_delete_section = (
        "Внимание! Вы собираетесь удалить раздел!\n"
        "Данное действие будет невозможно отменить\n"
        "Удаление раздела приведет к потере всех задач, записанных в этот раздел\n"
        "Вы точно хотите удалить раздел?"
    )
    delete_section = "Раздел {section} был успешно удален!\n" + CmdText.default
    no_delete_section = "Раздел не был удален!\n" + CmdText.default


class TaskText:
    hometask = (
        "Название: {title}\n\t\t"
        "Дедлайн: {deadline}\n\t\t"
        "Описание: {description}\n\t\t"
        "Напоминания: {notifications}\n\t\t"
        "Дата создания: {create_date}\n\t"
    )
    create = (
        "Отлично! Вы создали новое задание в разделе {section}\n"
        "Название для задания: {title}\n"
        "Дедлайн задания: {deadline}\n"
        "Описание к задаче: {description}\n"
    )
    no_task = (
        'Ой! Кажется никаких задач в разделе "{section}" нет!\n'
        "Хотите создать новую задачу?\n"
        'Нажмите кнопку "Создать новую задачу"'
    )
    no_one_task = "Ой! Кажется, у Вас нет ни одного записанного задания!"

    edit_name = "Введите новое название для предмета (желательно короткое)"

    enter_title = "Пожалуйста, введите название для новой задачи (рекомендуем короткое для удобства)"

    enter_deadline = (
        "Пожалуйста, укажите дедлайн (дату и время) задания\n"
        "Рекомендуется писать в обычном формате,\n"
        "Hапример 23 01 24, 12:00\n"
        "Либо нажмите любую из кнопок."
    )
    incorrect_deadline = (
        "Ой! Кажется вы ввели некорректный формат для времени!\n"
        "Пожалуйста, введите дедлайн в формате\n"
        "ДАТА МЕСЯЦ ГОД, для точного времени (если необходимо): ЧАС:МИНУТА"
    )

    enter_custom_deadline = "Введите свое значение для дедлайна\nОбязательно в минутах!"
    incorrect_custom_deadline = (
        "Ой! Кажется, вы неправильно ввели время для дедлайна!\n"
        + enter_custom_deadline
    )

    enter_description = (
        "Пожалуйста, укажите описание к задаче (одним сообщением до 1024х символов)"
    )

    incorrect_number = (
        "Ой! Кажется вы выбрали номер, которого нет в списке!\n"
        "Пожалуйста, повторите выбор"
    )

    edit_title = (
        'Название для задачи успешно изменено на "{new_title}"\n' + CmdText.default
    )
    edit_description = "Описание для задачи успешно обновлено\n" + CmdText.default
    edit_deadline = "Дедлайн задачи успешно изменен на {deadline}\n" + CmdText.default
    edit_deadline_with_notifications = (
        "Вы успешно изменили дедлайн задачи на {deadline}.\n"
        "Однако, у данной задачи были созданы напоминания\n"
        "({notifications})\n"
        "Вы можете выбрать новое время или оставить старое"
    )

    delete_task = "Задача успешно удалена!\n" + CmdText.default
    no_delete_task = "Задача не была удалена!\n" + CmdText.default

    @classmethod
    async def format_notifications(cls, notifications: list[NotificationModel]) -> str:
        if notifications is None or len(notifications) == 0:
            return "Без напоминаний"
        text = ""
        for notification in notifications:
            text += f"за {round((notification.deadline - notification.notification).total_seconds() // 60)} минут, "
        return text[:-2]

    @classmethod
    async def format_task(
        cls, task: TaskModel, notifications: list[NotificationModel]
    ) -> str:
        """
        "Название: {title}:\n\t\t"
        "Дедлайн: {deadline}\n\t\t"
        "Описание: {description}\n\t\t"
        "Напоминания: {notifications}\n\t\t"
        "Дата создания: {create_date}"
        """
        return cls.hometask.format(
            title=task.title,
            deadline=task.deadline if task.deadline else "Без дедлайна",
            description=task.description,
            notifications=await cls.format_notifications(notifications),
            create_date=task.create_date,
        )

    @classmethod
    async def format_all_tasks(cls, tasks: list[TaskModel]) -> tuple[int, str, dict]:
        k = 0
        text = ""
        state_data = {}
        for task in tasks:
            k += 1
            text += (
                f"{k}. "
                + cls.hometask.format(
                    title=task.title,
                    deadline=task.deadline if task.deadline else "Без дедлайна",
                    description=task.description,
                    notifications="",  # TODO notifications
                    create_date=task.create_date,
                )
                + "\n\n"
            )
            state_data[str(k)] = task.task_id
        return k, text, state_data


class NotificationText:
    ask_notification = "Хотите добавить напоминание?"
    add_notification = "Отлично! Теперь выберите за сколько минут до указанного времени напомнить Вам о задаче"
    add_custom_notification = "Пожалуйста, укажите свое время (В минутах!) за сколько нужно отправить уведомление"
    further_actions = (
        "Что будем делать дальше?\n"
        "В главное меню: /menu\n"
        "Создать еще один раздел: /new_section\n"
        "Перейти ко всем разделам: /sections\n"
        "Посмотреть все задачи: /tasks\n"
        "Либо нажмите на кнопку, чтобы создать еще одну задачу"
    )
    add_message = (
        "Хотите добавить сообщение для напоминания?\n"
        "Если да, то введите любое сообщение, которое будет отправлено Вам вместе с уведомлением\n"
        "Если нет, то нажмите кнопку"
    )
    created_notification = "Напоминание успешно создано!\n" + CmdText.default

    save_notifications = (
        "Все напоминания были сохранены и обновлены в соответствии с новым дедлайном\n"
        + CmdText.default
    )
    delete_many_notifications = "Все напоминания были удалены\n" + CmdText.default

    choose_update_action = "Выберите действие с напоминанием:"

    edit_time_notification = (
        "Время для напоминания успешно обновлено\n" + CmdText.default
    )
    incorrect_time_notification = (
        "Ой! Кажется, вы неправильно ввели время для напоминания!"
    )

    delete_notification = "Напоминание успешно удалено!\n" + CmdText.default
    no_delete_notification = "Напоминание не было удалено!" + CmdText.default


class Buttons:
    section_actions = [
        "Посмотреть все задачи",
        "Редактировать название",
        "Создать новую задачу",
        "Удалить раздел",
    ]
    task_actions = [
        "Изменить название",
        "Редактировать описание",
        "Изменить дедлайн",
        "Удалить задачу",
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
    # TODO для напоминания сделать кнопку напоминания в момент дедлайн
    add_notification = [
        "За 0 минут",
        "За 5 минут",
        "За 10 минут",
        "За 15 минут",
        "За 30 минут",
        "За 1 час",
        "Свое время",
    ]
    update_notifications_actions = [
        "Сохранить все напоминания",
        "Удалить все напоминания",
    ]
    notification_actions = [
        "Изменить время напоминания",
        "Удалить напоминание",
    ]
