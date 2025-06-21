from datetime import datetime, time, timedelta

def validate_date(date_text: str):
    if date_text is None or not date_text.strip():
        return None
    try:
        return datetime.strptime(date_text.strip(), "%d.%m.%y").date()
    except ValueError:
        return None

def validate_time(time_text: str):
    if time_text is None:
        return None
    try:
        return datetime.strptime(time_text.strip(), "%H:%M").time()
    except ValueError:
        return None
def get_current_time():
    return datetime.now().time()

def format_date(date_obj):
    if not date_obj:
        return "не указано"
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except Exception:
            return date_obj
    return date_obj.strftime("%d.%m.%Y")



def format_time(time_obj):
    if not time_obj:
        return ""
    if isinstance(time_obj, timedelta):
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return time(hour=hours, minute=minutes).strftime("%H:%M")
    if isinstance(time_obj, str):
        try:
            parsed_time = datetime.strptime(time_obj.strip(), "%H:%M").time()
            return parsed_time.strftime("%H:%M")
        except Exception:
            return time_obj
    return time_obj.strftime("%H:%M")

def format_task(task):
    lines = [f"📌 <b>{task.get('name', 'Без названия')}</b>"]
    if task.get('description'):
        lines.append(f"📝 {task['description']}")
    if task.get('deadline'):
        lines.append(f"⏳ Дедлайн: <i>{format_date(task['deadline'])}</i>")
    reminder_type_map = {
        "standard": "Стандартное",
        "custom": "Кастомное"
    }
    reminder_type_text = reminder_type_map.get(task.get('reminder_type'), task.get('reminder_type'))
    lines.append(f"🔔 Тип напоминания: <b>{reminder_type_text}</b>")

    if task.get('reminder_type') == 'standard':
        reminder_map = {
            'hourly': 'Каждый час',
            'daily': 'Каждый день',
            'weekly': 'Каждую неделю',
            'none': 'Без напоминания'
        }
        rem_text = reminder_map.get(task.get('custom_days'), 'Не задано')
        lines.append(f"⏰ Напоминание: <i>{rem_text}</i>")
    elif task.get('reminder_type') == 'custom':
        if task.get('custom_time'):
            lines.append(f"⏰ Время: <i>{format_time(task['custom_time'])}</i>")
        if task.get('custom_days'):
            lines.append(f"📅 Дни недели: <i>{task['custom_days']}</i>")
        if task.get('custom_dates'):
            dates = []
            for d in task['custom_dates'].split(','):
                try:
                    dt = datetime.strptime(d.strip(), "%Y-%m-%d").date()
                    dates.append(format_date(dt))
                except Exception:
                    dates.append(d.strip())
            lines.append(f"📆 Точные даты: <i>{', '.join(dates)}</i>")
    return "\n".join(lines)
