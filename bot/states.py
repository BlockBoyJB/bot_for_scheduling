from aiogram.fsm.state import State, StatesGroup


class UserActions(StatesGroup):
    create_user = State()
    delete_user = State()
    settings = State()


class SettingsActions(StatesGroup):
    edit_timezone = State()
    reformat_tasks = State()


class CreateSection(StatesGroup):
    choose_name = State()


class ChooseSection(StatesGroup):
    choose_section = State()
    choose_action = State()


class UpdateSection(StatesGroup):
    edit_name = State()
    delete_section = State()
    delete_tasks = State()


class CreateTask(StatesGroup):
    choose_section = State()
    enter_title = State()
    enter_deadline = State()

    enter_custom_deadline = State()
    enter_description = State()


class ChooseTask(StatesGroup):
    choose_task = State()
    choose_action = State()


class AllTasks(StatesGroup):
    delete_all_tasks = State()
    choose_delete_action = State()


class UpdateTask(StatesGroup):
    edit_title = State()
    edit_description = State()
    edit_deadline = State()
    delete_task = State()


class CreateNotification(StatesGroup):
    add_notification = State()
    add_time_notification = State()
    add_custom_time_notification = State()

    add_message = State()


class UpdateNotification(StatesGroup):
    update_notifications = State()

    edit_notifications = State()
    choose_action = State()

    edit_time_notification = State()
    delete_notification = State()
