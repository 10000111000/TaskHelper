START_TEXT = "Привет! Я TaskHelper бот для управления задачами."
HELP_TEXT = (
    "Используйте кнопки или команды для управления задачами.\n"
    "/add - добавить задачу\n"
    "/list - показать задачи"
)

BUTTON_ADD_TASK = "Добавить задачу"
BUTTON_LIST_TASKS = "Список задач"
BUTTON_CANCEL = "Отмена"
BUTTON_EDIT_TASK = "Редактировать задачу"
BUTTON_DELETE_TASK = "Удалить задачу"

PROMPT_TASK_NAME = "Введите название задачи:"
PROMPT_TASK_DESC = "Введите описание задачи (можно пропустить, отправив '.'):"
PROMPT_TASK_DEADLINE = "Введите дедлайн задачи в формате дд.мм.гг (можно пропустить, отправив '.'):"
PROMPT_REMINDER_TYPE_SELECT = "Выберите тип напоминания:"

REMINDER_TYPE_DEFAULT = "Стандартное"
REMINDER_TYPE_CUSTOM = "Кастомное"

DEFAULT_REMINDER_HOURLY = "Каждый час"
DEFAULT_REMINDER_DAILY = "Каждый день"
DEFAULT_REMINDER_WEEKLY = "Каждую неделю"
DEFAULT_REMINDER_NONE = "Без напоминания"

PROMPT_CUSTOM_DAYS = "Выберите дни недели для напоминания:"
PROMPT_CUSTOM_DATES = "Введите точные даты через запятую в формате дд.мм.гг (можно пропустить, отправив '.'):"
PROMPT_CUSTOM_TIME = "Введите время напоминания в формате ЧЧ:ММ (или '.' для текущего времени):"

CONFIRM_DELETE = "Вы уверены, что хотите удалить задачу  \"{task_name}\"?"
TASK_DELETED = "Задача удалена."
TASK_SAVED = "Задача сохранена."
ACTION_CANCELLED = "Действие отменено."
NO_TASKS = "Список задач пуст."
TASK_NOT_FOUND = "Задача не найдена."
SELECT_TASK_TO_EDIT = "Выберите задачу для редактирования:"
SELECT_TASK_TO_DELETE = "Выберите задачу для удаления:"

EDIT_PROMPT_NAME = "Введите новое название задачи (или '.' чтобы оставить текущее):"
EDIT_PROMPT_DESCRIPTION = "Введите новое описание задачи (или '.' чтобы оставить текущее / '..' чтобы очистить):"
EDIT_PROMPT_DEADLINE = "Введите новый дедлайн задачи в формате дд.мм.гг (или '.' чтобы оставить текущее / '..' чтобы очистить):"
EDIT_PROMPT_REMINDER_TYPE = "Выберите новый тип напоминания:"
EDIT_PROMPT_CUSTOM_TIME = "Введите новое время напоминания в формате ЧЧ:ММ (или '.' для текущего / '..' чтобы очистить):"
EDIT_PROMPT_CUSTOM_DAYS = "Выберите новые дни недели для напоминания (текущие: {current_days}):"
EDIT_PROMPT_CUSTOM_DATES = "Введите новые точные даты через запятую в формате дд.мм.гг (или '.' чтобы оставить текущие / '..' чтобы очистить):"

TASK_UPDATED = "Задача успешно обновлена!"

BUTTON_FAQ = "FAQ"

FAQ_TEXT = (
    "<b>О боте TaskHelper</b>\n\n"
    "Этот бот помогает управлять вашими задачами с напоминаниями.\n\n"
    "<b>Как использовать:</b>\n"
    "• Добавить задачу — нажмите кнопку «Добавить задачу» и следуйте подсказкам.\n"
    "• Список задач — просмотреть все ваши задачи.\n"
    "• Редактировать задачу — изменить параметры задачи.\n"
    "• Удалить задачу — удалить ненужную задачу.\n\n"
    "<b>Типы напоминаний:</b>\n"
    "• Стандартные: каждый час, каждый день или каждую неделю.\n"
    "• Кастомные: выбирайте дни недели или точные даты и время.\n\n"
    "Для отмены любого действия используйте кнопку «Отмена».\n"
    "Если при вводе описания, дедлайна или дат отправить точку «.», поле будет оставлено пустым."
)
