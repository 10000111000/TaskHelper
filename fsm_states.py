from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_reminder_type_selection = State()
    waiting_for_default_reminder_type = State()
    waiting_for_custom_days = State()
    waiting_for_custom_dates = State()
    waiting_for_custom_time = State()

class EditTaskStates(StatesGroup):
    waiting_for_task_selection = State()
    waiting_for_field_selection = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_reminder_type_selection = State()
    waiting_for_default_reminder_type = State()
    waiting_for_custom_days = State()
    waiting_for_custom_dates = State()
    waiting_for_custom_time = State()

class DeleteTaskStates(StatesGroup):
    waiting_for_task_selection = State()
    confirming_delete = State()
