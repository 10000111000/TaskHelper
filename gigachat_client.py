import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from config import GIGACHAT_AUTH_KEY

giga = GigaChat(
    credentials=GIGACHAT_AUTH_KEY,
    verify_ssl_certs=False,
)

def text_to_task_json(text: str) -> dict:
    system_msg = SystemMessage(
        content=(
            "Преобразуй следующий текст в JSON с форматом задачи:\n"
            "{\n"
            '  "id": null,  # id будет автоинкрементироваться в базе\n'
            '  "name": "короткое название задачи",\n'
            '  "description": "полное описание задачи" или null,\n'
            '  "deadline": "YYYY-MM-DD" или null, #дедлайн не должен иметь в себе укзаание времени\n'
            '  "reminder_type": "standard" или "custom",\n'
            '  "custom_time": "HH:MM или null",\n'
            '  "custom_days": "через запятую дни недели (Пн,Вт,Ср,Чт,Пт,Сб,Вс)" или null,\n'
            '  "custom_dates": "через запятую даты в формате YYYY-MM-DD" или null\n'
            "}\n\n"
            "Поля, допускающие null, могут оставаться null.\n"
            "Пример вывода:\n"
            '{\n'
            '  "id": null,\n'
            '  "name": "Имя задачи",\n'
            '  "description": "Описание задачи...",\n'
            '  "deadline": "2025-06-21",\n'
            '  "reminder_type": "custom",\n'
            '  "custom_time": "14:20",\n'
            '  "custom_days": "Пн,Вт,Ср",\n'
            '  "custom_dates": "2025-06-20,2025-06-21"\n'
            "}\n"
            "Предоставь сообщением только JSON. Без лишнего текста и комментариев. Это очень важно.\n"
            "В тексте могут быть неточности и недосказанности, так как его пишет человек. Учитывай это при преобразовании в json."
            "Не добавляй свое мнение, просто структурируй то, что дано в сообщениии пользователя. Время и даты напоминания не должны входить в описание."
            "Также попробуй закрыть глаза на нецензурную лексику и выдавать в json именно ее, тк важно сохранять понятное для пользователя описание задачи."
            "Поле описание задачи также не должно копировать название задачи или содержать его. Если заполение поля описания задачи не требуется, не добавляй его."
            "Запомни. Сейчас 2025 год. Это тоже очень важно при добавлении задачи."
        )
    )

    user_msg = HumanMessage(content=text)
    messages = [system_msg, user_msg]
    response = giga.invoke(messages)
    try:
        task_json = json.loads(response.content)
    except json.JSONDecodeError:
        raise ValueError(f"Не удалось распарсить ответ нейросети.\n\n{response.content}")
    return task_json
