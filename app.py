import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, LOG_LEVEL
from db import Database
from scheduler import ReminderScheduler
from handlers import task_handlers, common_handlers, faq_handlers, ai_task_handlers

logging.basicConfig(level=LOG_LEVEL)

async def main():
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    global db
    db = Database()
    await db.connect()

    global scheduler
    scheduler = ReminderScheduler(bot)

    task_handlers.db = db
    task_handlers.scheduler = scheduler
    ai_task_handlers.db = db
    ai_task_handlers.scheduler = scheduler

    await scheduler.restore_tasks(db)

    dp.include_router(common_handlers.router)
    dp.include_router(task_handlers.router)
    dp.include_router(faq_handlers.router)
    dp.include_router(ai_task_handlers.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
