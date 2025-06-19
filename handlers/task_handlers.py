from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fsm_states import TaskStates, EditTaskStates, DeleteTaskStates
from keyboards import (main_menu, cancel_keyboard, reminder_type_selection_keyboard,
                       default_reminder_options_keyboard, days_of_week_keyboard,
                       confirm_delete_keyboard, task_list_for_action_keyboard,
                       edit_task_options_keyboard)
from texts import *
from utils import validate_date, validate_time, format_task, get_current_time
from db import Database
from scheduler import ReminderScheduler

router = Router()
db = Database()
scheduler = None

@router.message(Command("add"))
@router.message(F.text == BUTTON_ADD_TASK)
async def add_task_start(message: Message, state: FSMContext):
    await state.set_state(TaskStates.waiting_for_name)
    await message.answer(PROMPT_TASK_NAME, reply_markup=cancel_keyboard())

@router.message(TaskStates.waiting_for_name)
async def add_task_name(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.clear()
        await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
        return
    await state.update_data(name=message.text)
    await state.set_state(TaskStates.waiting_for_description)
    await message.answer(PROMPT_TASK_DESC, reply_markup=cancel_keyboard())

@router.message(TaskStates.waiting_for_description)
async def add_task_description(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.clear()
        await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
        return
    desc = None if message.text.strip() == "." else message.text
    await state.update_data(description=desc)
    await state.set_state(TaskStates.waiting_for_deadline)
    await message.answer(PROMPT_TASK_DEADLINE, reply_markup=cancel_keyboard())

@router.message(TaskStates.waiting_for_deadline)
async def add_task_deadline(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.clear()
        await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
        return
    if message.text.strip() == ".":
        deadline = None
    else:
        deadline = validate_date(message.text)
        if message.text.strip() and not deadline:
            await message.answer("Неверный формат даты. Введите в формате дд.мм.гг, точку для пустого значения.")
            return
    await state.update_data(deadline=deadline)
    await state.set_state(TaskStates.waiting_for_reminder_type_selection)
    await message.answer(PROMPT_REMINDER_TYPE_SELECT, reply_markup=reminder_type_selection_keyboard())

@router.callback_query(TaskStates.waiting_for_reminder_type_selection, F.data.in_({"rem_type_default", "rem_type_custom"}))
async def reminder_type_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "rem_type_default":
        await state.update_data(reminder_type="standard")
        await state.set_state(TaskStates.waiting_for_default_reminder_type)
        await callback.message.answer("Выберите стандартное напоминание:", reply_markup=default_reminder_options_keyboard())
    else:
        await state.update_data(reminder_type="custom")
        await state.set_state(TaskStates.waiting_for_custom_days)
        await callback.message.answer(PROMPT_CUSTOM_DAYS, reply_markup=days_of_week_keyboard())

@router.callback_query(TaskStates.waiting_for_default_reminder_type, F.data.startswith("def_rem_"))
async def default_reminder_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    reminder_option = callback.data.replace("def_rem_", "")
    await state.update_data(custom_days=reminder_option)
    data = await state.get_data()
    task_id = await db.add_task(
        user_id=callback.from_user.id,
        name=data["name"],
        description=data.get("description"),
        deadline=data.get("deadline"),
        reminder_type=data["reminder_type"],
        custom_time=None,
        custom_days=data["custom_days"],
        custom_dates=None
    )
    task = await db.get_task(task_id, callback.from_user.id)
    if task:
        scheduler.schedule_task(task)
    await callback.message.answer(TASK_SAVED, reply_markup=main_menu())
    await state.clear()

@router.callback_query(TaskStates.waiting_for_custom_days, F.data.startswith("day_") | (F.data == "days_done"))
async def custom_days_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    selected = set(data.get("custom_days_temp", "").split(",")) if data.get("custom_days_temp") else set()
    if callback.data == "days_done":
        await state.update_data(custom_days=",".join(sorted(list(selected))) if selected else None)
        await state.set_state(TaskStates.waiting_for_custom_dates)
        await callback.message.answer(PROMPT_CUSTOM_DATES, reply_markup=cancel_keyboard())
        return
    day = callback.data[4:]
    if day in selected:
        selected.remove(day)
    else:
        selected.add(day)
    await state.update_data(custom_days_temp=",".join(sorted(list(selected))))
    await callback.message.edit_reply_markup(reply_markup=days_of_week_keyboard(selected))

@router.message(TaskStates.waiting_for_custom_dates)
async def custom_dates_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.clear()
        await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
        return
    dates_raw = message.text.strip()
    if not dates_raw or dates_raw == ".":
        dates_to_save = None
    else:
        dates_list = []
        for d in dates_raw.split(","):
            d = d.strip()
            dt = validate_date(d)
            if not dt:
                await message.answer("Неверный формат дат. Введите даты через запятую в формате дд.мм.гг или '.' для пустого значения.")
                return
            dates_list.append(dt.isoformat())
        dates_to_save = ",".join(dates_list)
    await state.update_data(custom_dates=dates_to_save)
    await state.set_state(TaskStates.waiting_for_custom_time)
    await message.answer(PROMPT_CUSTOM_TIME, reply_markup=cancel_keyboard())

@router.message(TaskStates.waiting_for_custom_time)
async def custom_time_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.clear()
        await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
        return
    time_input = message.text.strip()
    if time_input == ".":
        custom_time_to_save = get_current_time()
    else:
        t = validate_time(time_input)
        if not t:
            await message.answer("Неверный формат времени. Введите в формате ЧЧ:ММ или '.' для текущего времени.")
            return
        custom_time_to_save = t
    await state.update_data(custom_time=custom_time_to_save)
    data = await state.get_data()
    task_id = await db.add_task(
        user_id=message.from_user.id,
        name=data["name"],
        description=data.get("description"),
        deadline=data.get("deadline"),
        reminder_type=data["reminder_type"],
        custom_time=data["custom_time"],
        custom_days=data.get("custom_days"),
        custom_dates=data.get("custom_dates")
    )
    task = await db.get_task(task_id, message.from_user.id)
    if task:
        scheduler.schedule_task(task)
    await message.answer(TASK_SAVED, reply_markup=main_menu())
    await state.clear()

@router.message(Command("list"))
@router.message(F.text == BUTTON_LIST_TASKS)
async def list_tasks(message: Message):
    tasks = await db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer(NO_TASKS, reply_markup=main_menu())
        return
    for task in tasks:
        await message.answer(format_task(task), parse_mode="HTML")


@router.message(F.text == BUTTON_EDIT_TASK)
async def edit_task_list(message: Message, state: FSMContext):
    tasks = await db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer(NO_TASKS, reply_markup=main_menu())
        return
    await state.set_state(EditTaskStates.waiting_for_task_selection)
    await message.answer(SELECT_TASK_TO_EDIT, reply_markup=task_list_for_action_keyboard(tasks, "edit"))

@router.callback_query(EditTaskStates.waiting_for_task_selection, F.data.startswith("edit_"))
async def edit_task_select(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    task_id = int(callback.data.split("_")[1])
    task = await db.get_task(task_id, callback.from_user.id)
    if not task:
        await callback.message.answer(TASK_NOT_FOUND, reply_markup=main_menu())
        await state.clear()
        return
    await state.update_data(current_task_id=task_id, editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await callback.message.answer(f"Что хотите отредактировать в задаче #{task_id} \"{task['name']}\"?\n\nТекущие данные:\n{format_task(task)}",
                                  reply_markup=edit_task_options_keyboard(), parse_mode="HTML")

@router.callback_query(EditTaskStates.waiting_for_field_selection, F.data.startswith("edit_field_"))
async def edit_field_select(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    field = callback.data.replace("edit_field_", "")
    data = await state.get_data()
    task = data["editing_task_data"]
    if field == "done":
        await db.update_task(data["current_task_id"], callback.from_user.id,
                             name=task['name'],
                             description=task['description'],
                             deadline=task['deadline'],
                             reminder_type=task['reminder_type'],
                             custom_time=task['custom_time'],
                             custom_days=task['custom_days'],
                             custom_dates=task['custom_dates'])
        updated_task = await db.get_task(data["current_task_id"], callback.from_user.id)
        if updated_task:
            scheduler.schedule_task(updated_task)
        await callback.message.answer(TASK_UPDATED, reply_markup=main_menu())
        await state.clear()
        return
    await state.update_data(editing_field=field)
    if field == "name":
        await state.set_state(EditTaskStates.waiting_for_name)
        await callback.message.answer(EDIT_PROMPT_NAME, reply_markup=cancel_keyboard())
    elif field == "description":
        await state.set_state(EditTaskStates.waiting_for_description)
        await callback.message.answer(EDIT_PROMPT_DESCRIPTION, reply_markup=cancel_keyboard())
    elif field == "deadline":
        await state.set_state(EditTaskStates.waiting_for_deadline)
        await callback.message.answer(EDIT_PROMPT_DEADLINE, reply_markup=cancel_keyboard())
    elif field == "reminder_type":
        await state.set_state(EditTaskStates.waiting_for_reminder_type_selection)
        await callback.message.answer(EDIT_PROMPT_REMINDER_TYPE, reply_markup=reminder_type_selection_keyboard())
    elif field == "custom_time":
        await state.set_state(EditTaskStates.waiting_for_custom_time)
        await callback.message.answer(EDIT_PROMPT_CUSTOM_TIME, reply_markup=cancel_keyboard())
    elif field == "custom_days":
        await state.set_state(EditTaskStates.waiting_for_custom_days)
        current_days_str = task.get('custom_days', '') or 'не заданы'
        await callback.message.answer(EDIT_PROMPT_CUSTOM_DAYS.format(current_days=current_days_str), reply_markup=days_of_week_keyboard(current_days_str.split(',') if current_days_str else None))
    elif field == "custom_dates":
        await state.set_state(EditTaskStates.waiting_for_custom_dates)
        await callback.message.answer(EDIT_PROMPT_CUSTOM_DATES, reply_markup=cancel_keyboard())

@router.message(EditTaskStates.waiting_for_name)
async def edit_name_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await message.answer("Изменение отменено.", reply_markup=edit_task_options_keyboard())
        return
    data = await state.get_data()
    task = data["editing_task_data"]
    if message.text.strip() != ".":
        task['name'] = message.text.strip()
    await state.update_data(editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await message.answer("Название обновлено.", reply_markup=edit_task_options_keyboard())

@router.message(EditTaskStates.waiting_for_description)
async def edit_description_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await message.answer("Изменение отменено.", reply_markup=edit_task_options_keyboard())
        return
    data = await state.get_data()
    task = data["editing_task_data"]
    if message.text.strip() == "..":
        task['description'] = None
    elif message.text.strip() != ".":
        task['description'] = message.text.strip()
    await state.update_data(editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await message.answer("Описание обновлено.", reply_markup=edit_task_options_keyboard())

@router.message(EditTaskStates.waiting_for_deadline)
async def edit_deadline_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await message.answer("Изменение отменено.", reply_markup=edit_task_options_keyboard())
        return
    data = await state.get_data()
    task = data["editing_task_data"]
    if message.text.strip() == "..":
        task['deadline'] = None
    elif message.text.strip() != ".":
        deadline = validate_date(message.text)
        if not deadline:
            await message.answer("Неверный формат даты. Введите в формате дд.мм.гг, '.' чтобы оставить, '..' чтобы очистить.")
            return
        task['deadline'] = deadline
    await state.update_data(editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await message.answer("Дедлайн обновлен.", reply_markup=edit_task_options_keyboard())

@router.callback_query(EditTaskStates.waiting_for_reminder_type_selection, F.data.in_({"rem_type_default", "rem_type_custom"}))
async def edit_reminder_type_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    task = data["editing_task_data"]
    if callback.data == "rem_type_default":
        task['reminder_type'] = "standard"
        task['custom_time'] = None
        task['custom_days'] = None
        task['custom_dates'] = None
        await state.update_data(editing_task_data=task)
        await state.set_state(EditTaskStates.waiting_for_default_reminder_type)
        await callback.message.answer("Выберите стандартное напоминание:", reply_markup=default_reminder_options_keyboard())
    else:
        task['reminder_type'] = "custom"
        await state.update_data(editing_task_data=task)
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await callback.message.answer("Тип напоминания изменен на 'Кастомное'. Отредактируйте остальные поля для кастомных напоминаний.",
                                      reply_markup=edit_task_options_keyboard())

@router.callback_query(EditTaskStates.waiting_for_default_reminder_type, F.data.startswith("def_rem_"))
async def edit_default_reminder_selected(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    reminder_option = callback.data.replace("def_rem_", "")
    data = await state.get_data()
    task = data["editing_task_data"]
    task['custom_days'] = reminder_option
    await state.update_data(editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await callback.message.answer("Стандартное напоминание обновлено.", reply_markup=edit_task_options_keyboard())

@router.callback_query(EditTaskStates.waiting_for_custom_days, F.data.startswith("day_") | (F.data == "days_done"))
async def edit_custom_days_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    task = data["editing_task_data"]
    selected = set(data.get("custom_days_temp", task.get('custom_days', '')).split(",")) if data.get("custom_days_temp") or task.get('custom_days') else set()
    if callback.data == "days_done":
        task['custom_days'] = ",".join(sorted(list(selected))) if selected else None
        await state.update_data(editing_task_data=task)
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await callback.message.answer("Дни недели напоминания обновлены.", reply_markup=edit_task_options_keyboard())
        return
    day = callback.data[4:]
    if day in selected:
        selected.remove(day)
    else:
        selected.add(day)
    await state.update_data(custom_days_temp=",".join(sorted(list(selected))))
    await callback.message.edit_reply_markup(reply_markup=days_of_week_keyboard(selected))

@router.message(EditTaskStates.waiting_for_custom_dates)
async def edit_custom_dates_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await message.answer("Изменение отменено.", reply_markup=edit_task_options_keyboard())
        return
    data = await state.get_data()
    task = data["editing_task_data"]
    dates_raw = message.text.strip()
    if dates_raw == "..":
        task['custom_dates'] = None
    elif dates_raw == ".":
        pass
    else:
        dates_list = []
        for d in dates_raw.split(","):
            d = d.strip()
            dt = validate_date(d)
            if not dt:
                await message.answer("Неверный формат дат. Введите даты через запятую в формате дд.мм.гг, '.' чтобы оставить, '..' чтобы очистить.")
                return
            dates_list.append(dt.isoformat())
        task['custom_dates'] = ",".join(dates_list)
    await state.update_data(editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await message.answer("Точные даты напоминания обновлены.", reply_markup=edit_task_options_keyboard())

@router.message(EditTaskStates.waiting_for_custom_time)
async def edit_custom_time_input(message: Message, state: FSMContext):
    if message.text == BUTTON_CANCEL:
        await state.set_state(EditTaskStates.waiting_for_field_selection)
        await message.answer("Изменение отменено.", reply_markup=edit_task_options_keyboard())
        return
    data = await state.get_data()
    task = data["editing_task_data"]
    time_input = message.text.strip()
    if time_input == "..":
        task['custom_time'] = None
    elif time_input == ".":
        task['custom_time'] = get_current_time()
    else:
        t = validate_time(time_input)
        if not t:
            await message.answer("Неверный формат времени. Введите в формате ЧЧ:ММ, '.' для текущего, '..' для очистки.")
            return
        task['custom_time'] = t
    await state.update_data(editing_task_data=task)
    await state.set_state(EditTaskStates.waiting_for_field_selection)
    await message.answer("Время напоминания обновлено.", reply_markup=edit_task_options_keyboard())

@router.message(F.text == BUTTON_DELETE_TASK)
async def delete_task_list(message: Message, state: FSMContext):
    tasks = await db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer(NO_TASKS, reply_markup=main_menu())
        return
    await state.set_state(DeleteTaskStates.waiting_for_task_selection)
    await message.answer(SELECT_TASK_TO_DELETE, reply_markup=task_list_for_action_keyboard(tasks, "delete"))

@router.callback_query(DeleteTaskStates.waiting_for_task_selection, F.data.startswith("delete_"))
async def delete_task_select(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    task_id = int(callback.data.split("_")[1])
    task = await db.get_task(task_id, callback.from_user.id)
    if not task:
        await callback.message.answer(TASK_NOT_FOUND, reply_markup=main_menu())
        await state.clear()
        return
    await state.update_data(task_to_delete_id=task_id, task_to_delete_name=task['name'])
    await state.set_state(DeleteTaskStates.confirming_delete)
    await callback.message.answer(CONFIRM_DELETE.format(task_id=task_id, task_name=task['name']), reply_markup=confirm_delete_keyboard())

@router.callback_query(DeleteTaskStates.confirming_delete, F.data.in_({"delete_yes", "delete_no"}))
async def delete_task_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "delete_yes":
        data = await state.get_data()
        task_id = data["task_to_delete_id"]
        await db.delete_task(task_id, callback.from_user.id)
        scheduler.remove_task(task_id)
        await callback.message.answer(TASK_DELETED, reply_markup=main_menu())
    else:
        await callback.message.answer(ACTION_CANCELLED, reply_markup=main_menu())
    await state.clear()

@router.message(Command("cancel"))
@router.message(F.text == BUTTON_CANCEL)
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(ACTION_CANCELLED, reply_markup=main_menu())