from bot.db import NotificationModel, TaskModel

from .timezone import TimezoneService


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
        "Создать новую задачу: /new_task\n"
        "Помощь: /help"
    )
    help = (
        "Помощь\n"
        "Этот бот создан для отслеживания задач.\n"
        'Работает по принципу "предмет(тема) -> задачи",\n'
        "то есть вы можете создавать определенные разделы и внутри них создавать тематические задачки.\n"
        'Например: создаем раздел "Домашние дела" и внутри него создаем задачу "Покормить кота".\n\n'
        "Существуют следущие команды:\n"
        "/sections - посмотреть все разделы, которые вы создали. Здесь вы можете:\n"
        "\t- Посмотреть все созданные задачи и редактировать их\n\t- Редактировать название\n"
        "\t- Создать новую задачу\n\t- Удалить все задачи, сохранив раздел\n\t- Удалить раздел вместе с задачами\n"
        "/new_section - создать новый раздел\n"
        "/menu - главное меню\n"
        "/tasks - посмотреть все задачи, которые вы создали (по всем разделам)\n"
        "/new_task - создать новую задачу\n"
        "/settings - настройки. Здесь вы можете:\n"
        "\t- Изменить часовой пояс"
    )

    default = "К разделам: /sections\nВ главное меню: /menu\nСоздать задачу: /new_task\nСоздать раздел: /new_section"

    incorrect_btn = "Пожалуйста, выбирайте только из доступных ниже кнопок!"


class SettingsText:
    add_tz = (
        "Пожалуйста, введите Ваш часовой пояс относительно UTC\n"
        'Например: "+2" или "-4"'
    )
    incorrect_tz = "Ой! Кажется, Вы ввели неправильный часовой пояс!\n" + add_tz

    edit_timezone_with_tasks = (
        "Вы собираетесь изменить часовой пояс, "
        "однако у Вас есть задачи, дедлайны которых сохранены в старом часовом поясе.\n"
        "При изменении часового пояса задачи, у которых есть дедлайн будут отображаться в другом времени\n"
        "Например задача в 15:00 в часовом поясе UTC+5 при смене пояса на UTC+3 будет отображаться как 12:00\n"
        "Выберите одно из действий и нажмите на кнопку"
    )

    update_timezone = "Часовой пояс успешно изменен\n" + CmdText.default
    update_tz_with_tasks = (
        "Все задачи и напоминания были обновлены в соответствии с новым часовым поясом.\n"
        "Внимание! Некоторые напоминания могли быть удалены в связи с истекшим временем "
        "(изменение дедлайна могло сместить время напоминания в прошлое).\n"
        "Рекомендуется проверить все задачи командой /tasks"
    )
    update_tz_without_tasks = (
        "Все задачи сохранены с новым часовым поясом без внесения изменений\n"
        + CmdText.default
    )


class UserText:
    create = (
        "Приветствуем в нашем телеграм боте для планирования задач!\n"
        "Пожалуйста, введите Ваш часовой пояс относительно UTC, чтобы Вам было удобнее создавать задачи и напоминания\n"
        'Например: "+2" или "-4"\n'
        'Вы можете пропустить этот шаг, нажав на кнопку "Пропустить"\n'
        "У Вас будет возможность добавить/изменить часовой пояс в /settings -> изменить пояс"
    )

    user_created = (
        "Пользователь успешно создан!\n"
        "Для дальнейшей работы рекомендуем создать раздел для задач или обратиться за помощью\n"
        "Создать новый раздел: /new_section\n"
        "В главное меню: /menu\n"
        "Помощь: /help\n"
    )

    confirm_delete = (
        "Вы собираетесь остановить бота! "
        "Это действие удалит всю информацию о Вас в нашей системе, включая разделы, задачи и напоминания\n"
        "Чтоб снова воспользоваться ботом, нужно будет нажать команду /start\n"
        "Вы уверены, что хотите остановить бота?"
    )

    user_deleted = (
        "Вся информация о пользователе удалена!\n"
        "Чтобы снова воспользоваться ботом, нажмите /start"
    )

    user_not_deleted = "Пользователь не был удален!\n" + CmdText.default

    settings = (
        "Вы находитесь в настройках. Вы можете:\n"
        'Изменить часовой пояс: "Изменить пояс"\n'
        "Чтобы выбрать действие, нажмите на одну из кнопок ниже:\n"
    )
    add_tz = (
        "Пожалуйста, введите Ваш часовой пояс относительно UTC\n"
        'Например: "+2" или "-4"'
    )
    incorrect_tz = "Ой! Кажется, Вы ввели неправильный часовой пояс!\n" + add_tz

    edit_timezone_with_tasks = (
        "Вы собираетесь изменить часовой пояс, "
        "однако у Вас есть задачи, дедлайны которых сохранены в старом часовом поясе.\n"
        "При изменении часового пояса задачи, у которых есть дедлайн будут отображаться в другом времени\n"
        "Например задача в 15:00 в часовом поясе UTC+5 при смене пояса на UTC+3 будет отображаться как 12:00\n"
        "Выберите одно из действий и нажмите на кнопку"
    )

    update_timezone = "Часовой пояс успешно изменен\n" + CmdText.default
    update_tz_with_tasks = (
        "Все задачи и напоминания были обновлены в соответствии с новым часовым поясом.\n"
        "Внимание! Некоторые напоминания могли быть удалены в связи с истекшим временем "
        "(изменение дедлайна могло сместить время напоминания в прошлое).\n"
        "Рекомендуется проверить все задачи командой /tasks"
    )
    update_tz_without_tasks = (
        "Все задачи сохранены с новым часовым поясом без внесения изменений\n"
        + CmdText.default
    )


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
    confirm_delete_tasks = (
        "Внимание! Вы собираетесь удалить все задачи из раздела {section}!\n"
        "Данное действие будет невозможно отменить\n"
        "Вы точно хотите удалить все задачи из раздела?"
    )
    delete_section = "Раздел {section} был успешно удален!\n" + CmdText.default
    no_delete_section = "Раздел не был удален!\n" + CmdText.default
    delete_tasks_section = "Все задачи из раздела {section} были удалены!\n" + CmdText.default
    no_delete_tasks_section = "Задачи не были удалены!\n" + CmdText.default


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
        "Время нужно указывать по московскому времени, если Вы не указывали свой часовой пояс!\n"
        "В противном случае указывайте время в своем часовом поясе!\n"
        "Рекомендуется писать в обычном формате,\n"
        "Hапример 23 01 24, 12:00\n"
        "Либо нажмите любую из кнопок."
    )
    incorrect_deadline = (
        "Ой! Кажется вы ввели некорректный формат для времени!\n"
        "Пожалуйста, введите дедлайн в формате\n"
        "ДАТА МЕСЯЦ ГОД, для точного времени (если необходимо): ЧАС:МИНУТА\n"
        "Время указывать по московскому времени!"
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

    delete_all_tasks = (
        "Внимание! Вы собираетесь удалить все существующие задачи! "
        "Данное действие будет невозможно отменить\n"
        "Вы можете удалить все задачи вместе с существующими разделами, "
        "либо удалить все задачи, сохранив разделы"
    )

    @classmethod
    def format_notifications(cls, notifications: list[NotificationModel]) -> str:
        if notifications is None or len(notifications) == 0:
            return "Без напоминаний"
        text = ""
        for notification in notifications:
            text += f"за {round((notification.deadline - notification.notification).total_seconds() // 60)} минут, "
        return text[:-2]

    @classmethod
    def format_task(
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
            deadline=TimezoneService.convert_to_tz(task.deadline, task.timezone)
            if task.deadline
            else "Без дедлайна",
            description=task.description,
            notifications=cls.format_notifications(notifications),
            create_date=task.create_date,
        )


class NotificationText:
    ask_notification = "Хотите добавить напоминание?"
    add_notification = "Отлично! Теперь выберите за сколько минут до указанного времени напомнить Вам о задаче"
    add_custom_notification = "Пожалуйста, укажите свое время (В минутах!) за сколько нужно отправить уведомление"
    incorrect_time = (
        "Ой! Кажется, Вы выбрали время для напоминания, которое уже прошло: сообщение с напоминанием не придёт!\n"
        "Пожалуйста, повторите свой выбор!"
    )
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
    save_some_notifications = (
        "Напоминания сохранены и обновлены в соответствии с новым дедлайном.\n"
        "Однако следующие напоминания были удалены в связи с истекшим временем напоминания.\n"
        "(Вы изменили дедлайн так, что эти напоминания должны были сработать в прошом):\n\t"
    )
    delete_many_notifications = "Все напоминания были удалены\n" + CmdText.default

    choose_update_action = "Выберите действие с напоминанием:"

    edit_time_notification = (
        "Время для напоминания успешно обновлено\n" + CmdText.default
    )
    incorrect_input_time = "Ой! Кажется, вы неправильно ввели время для напоминания!"

    delete_notification = "Напоминание успешно удалено!\n" + CmdText.default
    no_delete_notification = "Напоминание не было удалено!" + CmdText.default


class Buttons:
    section_actions = [
        "Посмотреть все задачи",
        "Редактировать название",
        "Создать новую задачу",
        "Удалить все задачи",
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
    all_tasks_actions = [
        "Сохранить разделы",
        "Удалить разделы",
        "Отменить",
    ]
    settings = [
        "Изменить пояс",
    ]
    edit_timezone_actions = ["Перенести все задачи", "Оставить без изменений"]
