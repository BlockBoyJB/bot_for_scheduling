from aiogram.fsm.state import State, StatesGroup


class CreateSubject(StatesGroup):
    choose_name = State()


class ChooseSubject(StatesGroup):
    choose_subject = State()
    choose_action = State()


class CreateHometask(StatesGroup):
    enter_title = State()
    enter_deadline = State()
    set_custom_deadline = State()
    enter_description = State()
    add_notification = State()
    set_time = State()
    set_custom_time = State()


class ChooseHometask(StatesGroup):
    choose_hometask = State()
    choose_action = State()

    edit_title = State()
    edit_description = State()
    edit_deadline = State()
    delete_task = State()


class HometaskNotification(StatesGroup):
    update_notifications = State()
    choose_update_action = State()
    new_notification_time = State()
    edit_notification = State()


class EditSubject(StatesGroup):
    edit_name = State()
    delete_subject = State()
