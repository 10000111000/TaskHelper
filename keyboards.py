from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import texts


def main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить задачу")],
            [KeyboardButton(text="Список задач")],
            [KeyboardButton(text="Редактировать задачу"), KeyboardButton(text="Удалить задачу")],
            [KeyboardButton(text="Добавить задачу c помощью GigaChat (возможны ошибки)")],
            [KeyboardButton(text=texts.BUTTON_FAQ)]
        ],
        resize_keyboard=True
    )
    return kb
def cancel_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

def reminder_type_selection_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Стандартное", callback_data="rem_type_default"),
            InlineKeyboardButton(text="Кастомное", callback_data="rem_type_custom")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def default_reminder_options_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Каждый час", callback_data="def_rem_hourly")],
        [InlineKeyboardButton(text="Каждый день", callback_data="def_rem_daily")],
        [InlineKeyboardButton(text="Каждую неделю", callback_data="def_rem_weekly")],
        [InlineKeyboardButton(text="Без напоминания", callback_data="def_rem_none")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def days_of_week_keyboard(selected=None):
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons = []
    current_row = []
    for i, day in enumerate(days):
        text = f"✅{day}" if selected and day in selected else day
        current_row.append(InlineKeyboardButton(text=text, callback_data=f"day_{day}"))
        if len(current_row) == 4:
            buttons.append(current_row)
            current_row = []
    if current_row:
        buttons.append(current_row)

    buttons.append([InlineKeyboardButton(text="Готово", callback_data="days_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def confirm_delete_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Да", callback_data="delete_yes"),
            InlineKeyboardButton(text="Нет", callback_data="delete_no")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def task_list_for_action_keyboard(tasks, action_prefix="edit"):
    buttons = []
    for task in tasks:
        buttons.append(
            [InlineKeyboardButton(text=f"{task['name']}", callback_data=f"{action_prefix}_{task['id']}")]
        )
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def edit_task_options_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Название", callback_data="edit_field_name")],
        [InlineKeyboardButton(text="Описание", callback_data="edit_field_description")],
        [InlineKeyboardButton(text="Дедлайн", callback_data="edit_field_deadline")],
        [InlineKeyboardButton(text="Тип напоминания", callback_data="edit_field_reminder_type")],
        [InlineKeyboardButton(text="Время напоминания", callback_data="edit_field_custom_time")],
        [InlineKeyboardButton(text="Дни недели напоминания", callback_data="edit_field_custom_days")],
        [InlineKeyboardButton(text="Точные даты напоминания", callback_data="edit_field_custom_dates")],
        [InlineKeyboardButton(text="Готово", callback_data="edit_field_done")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить"), KeyboardButton(text="Отменить")]
        ],
        resize_keyboard=True
    )