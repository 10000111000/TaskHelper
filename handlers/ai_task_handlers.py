from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime

from fsm_states import TaskStates
from keyboards import cancel_keyboard, confirm_keyboard, main_menu
from utils import validate_date, validate_time, format_task
from db import Database
from scheduler import ReminderScheduler
from gigachat_client import text_to_task_json
from texts import ACTION_CANCELLED
router = Router()

db: Database = None
scheduler: ReminderScheduler = None

@router.message(Command("ai_add"))
@router.message(F.text == "Добавить задачу c помощью GigaChat (возможны ошибки)")
async def ai_add_start(message: Message, state: FSMContext):
    await state.set_state(TaskStates.waiting_for_ai_input)
    await message.answer(
        "Отправьте текстовое сообщение с описанием задачи для ИИ.",
        reply_markup=cancel_keyboard()
    )

@router.message(TaskStates.waiting_for_ai_input)
async def ai_input_handler(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer("Добавление задачи отменено.", reply_markup=cancel_keyboard())
        await state.clear()
        return

    user_id = message.from_user.id
    user_text = message.text

    await message.answer("Обрабатываю запрос... Пожалуйста, подождите.")

    try:
        task_data = text_to_task_json(user_text)
    except Exception as e:
        await message.answer(f"Ошибка при обработке ИИ. Попробуйте снова.")
        await state.clear()
        return

    await state.update_data(ai_task=task_data)

    preview_text = "<b>Предпросмотр задачи:</b>\n\n" + format_task(task_data)
    await state.set_state(TaskStates.waiting_for_ai_confirmation)
    await message.answer(preview_text, parse_mode="HTML", reply_markup=confirm_keyboard())

@router.message(TaskStates.waiting_for_ai_confirmation)
async def ai_confirm_handler(message: Message, state: FSMContext):
    text = message.text.lower()
    if text == "подтвердить":
        data = await state.get_data()
        task_data = data.get("ai_task")
        if not task_data:
            await message.answer("Нет данных задачи. Попробуйте добавить заново.")
            await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
            await state.clear()
            return

        deadline = validate_date(task_data.get("deadline"))
        custom_time = validate_time(task_data.get("custom_time"))

        task_id = await db.add_task(
            user_id=message.from_user.id,
            name=task_data.get("name"),
            description=task_data.get("description"),
            deadline=deadline,
            reminder_type=task_data.get("reminder_type"),
            custom_days=task_data.get("custom_days"),
            custom_dates=task_data.get("custom_dates"),
            custom_time=custom_time
        )

        task = await db.get_task(task_id, message.from_user.id)
        if task:
            scheduler.schedule_task(task)
            await message.answer("Задача успешно создана и напоминания запланированы.", reply_markup=main_menu())
        else:
            await message.answer("Ошибка при сохранении задачи.", reply_markup=main_menu())
        await state.clear()

    elif text == "отменить":
        await message.answer(ACTION_CANCELLED, reply_markup=main_menu())
        await state.clear()
    else:
        await message.answer("Пожалуйста, выберите 'Подтвердить' или 'Отменить'.")
