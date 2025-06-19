from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, time, timedelta

def timedelta_to_time(td: timedelta) -> time:
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def schedule_task(self, task):
        job_id_prefix = f"task_{task['id']}"
        self.remove_task(task['id'])
        if task['reminder_type'] == 'standard':
            if task['custom_days'] == 'hourly':
                self.scheduler.add_job(
                    self.send_reminder,
                    trigger=CronTrigger(minute=0),
                    args=[task],
                    id=f"{job_id_prefix}_hourly"
                )
            elif task['custom_days'] == 'daily':
                self.scheduler.add_job(
                    self.send_reminder,
                    trigger=CronTrigger(hour=9, minute=0),
                    args=[task],
                    id=f"{job_id_prefix}_daily"
                )
            elif task['custom_days'] == 'weekly':
                self.scheduler.add_job(
                    self.send_reminder,
                    trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                    args=[task],
                    id=f"{job_id_prefix}_weekly"
                )
        elif task['reminder_type'] == 'custom':
            if task['custom_time']:
                custom_time = task['custom_time']
                if isinstance(custom_time, timedelta):
                    custom_time = timedelta_to_time(custom_time)
                if task['custom_days']:
                    days = task['custom_days'].split(',')
                    days_map = {'Пн': 'mon', 'Вт': 'tue', 'Ср': 'wed', 'Чт': 'thu', 'Пт': 'fri', 'Сб': 'sat', 'Вс': 'sun'}
                    for day in days:
                        day_eng = days_map.get(day)
                        if day_eng:
                            self.scheduler.add_job(
                                self.send_reminder,
                                trigger=CronTrigger(day_of_week=day_eng, hour=custom_time.hour, minute=custom_time.minute),
                                args=[task],
                                id=f"{job_id_prefix}_{day_eng}"
                            )
                if task['custom_dates']:
                    for date_str in task['custom_dates'].split(','):
                        try:
                            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
                            run_datetime = datetime.combine(dt, custom_time)
                            if run_datetime > datetime.now():
                                self.scheduler.add_job(
                                    self.send_reminder,
                                    trigger=DateTrigger(run_date=run_datetime),
                                    args=[task],
                                    id=f"{job_id_prefix}_{date_str.strip().replace('-', '')}"
                                )
                        except Exception:
                            continue

    def remove_task(self, task_id):
        job_id_prefix = f"task_{task_id}"
        for job in self.scheduler.get_jobs():
            if job.id.startswith(job_id_prefix):
                self.scheduler.remove_job(job.id)

    async def send_reminder(self, task):
        try:
            text = f"Напоминание о задаче:\n{task['name']}\n"
            if task['description']:
                text += f"Описание: {task['description']}\n"
            if task['deadline']:
                text += f"Дедлайн: {task['deadline'].strftime('%d.%m.%y')}\n"
            text += "Не забудьте выполнить!"
            await self.bot.send_message(task['user_id'], text)
        except Exception:
            pass

    async def restore_tasks(self, db):
        tasks = await db.get_all_tasks()
        if not tasks:
            return
        for task in tasks:
            from datetime import datetime, time
            if isinstance(task.get('deadline'), str):
                try:
                    task['deadline'] = datetime.strptime(task['deadline'], "%d.%m.%Y %H:%M")
                except Exception:
                    try:
                        task['deadline'] = datetime.strptime(task['deadline'], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        task['deadline'] = None
            if isinstance(task.get('custom_time'), str):
                try:
                    h, m = map(int, task['custom_time'].split(':')[:2])
                    task['custom_time'] = time(hour=h, minute=m)
                except Exception:
                    task['custom_time'] = None
            self.schedule_task(task)