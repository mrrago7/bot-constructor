# Конструктор GPT-ботов

Учебный проект на Django и Django REST Framework. Позволяет создавать ботов, настраивать сценарии общения с пользователями и обрабатывать сообщения через GPT.

## Возможности

- CRUD-операции для ботов.
- CRUD-операции для сценариев.
- Создание и управление шагами сценариев.
- Связь шагов между собой для построения последовательного диалога.
- Обработка сообщений через GPT API.
- Сохранение состояния диалога между сообщениями.
- Управление данными через Django Admin.
- Автоматические API-тесты.

## Технологии

- Python 3.12
- Django 6.1
- Django REST Framework
- OpenAI API
- SQLite
- pip-tools

## Установка и запуск

1. Клонировать репозиторий:

```bash
git clone https://github.com/mrrago7/bot-constructor.git
cd bot-constructor
```

2. Создать виртуальное окружение:

```bash
python -m venv .venv
```

3. Активировать окружение в Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Установить pip-tools:

```bash
python -m pip install pip-tools
```

5. Установить зависимости:

```bash
pip-compile requirements.in
pip-sync requirements.txt
```

6. Применить миграции:

```bash
python manage.py migrate
```

7. Создать администратора:

```bash
python manage.py createsuperuser
```

8. Запустить сервер:

```bash
python manage.py runserver
```

API будет доступно по адресу `http://127.0.0.1:8000/api/`.

Панель администратора: `http://127.0.0.1:8000/admin/`.

## Настройка GPT

По умолчанию проект работает в тестовом режиме (`OPENAI_MOCK_MODE = True`). В этом режиме возвращается тестовый ответ, поэтому API-ключ и оплата запросов не требуются.

Для использования реального OpenAI API необходимо установить `OPENAI_MOCK_MODE = False` в настройках проекта и указать API-ключ в файле `.env`:

```text
OPENAI_API_KEY=your_api_key
```

## API

### Боты

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/bots/` | Получить список ботов |
| POST | `/api/bots/` | Создать бота |
| GET | `/api/bots/{id}/` | Получить бота |
| PUT | `/api/bots/{id}/` | Обновить бота |
| DELETE | `/api/bots/{id}/` | Удалить бота |

Пример создания бота:

```json
{
    "name": "Мой бот",
    "description": "Тестовый бот",
    "owner": 1
}
```

### Сценарии

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/scenarios/` | Получить список сценариев |
| POST | `/api/scenarios/` | Создать сценарий |
| GET | `/api/scenarios/{id}/` | Получить сценарий |
| PUT | `/api/scenarios/{id}/` | Обновить сценарий |
| DELETE | `/api/scenarios/{id}/` | Удалить сценарий |
| GET | `/api/scenarios/{id}/steps/` | Получить шаги сценария |

### Шаги сценариев

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/scenarios/{id}/steps/` | Получить шаги сценария |
| POST | `/api/scenarios/{id}/steps/` | Добавить шаг |
| GET | `/api/scenarios/{id}/steps/{step_id}/` | Получить шаг |
| PUT | `/api/scenarios/{id}/steps/{step_id}/` | Обновить шаг |
| DELETE | `/api/scenarios/{id}/steps/{step_id}/` | Удалить шаг |

Также доступен отдельный CRUD для шагов через `/api/steps/`.

### Общение с ботом

`POST /api/bots/{id}/chat/`

Пример запроса:

```json
{
    "message": "Привет!"
}
```

Для продолжения существующего диалога необходимо передать `conversation_id`, полученный в предыдущем ответе:

```json
{
    "message": "Продолжим",
    "conversation_id": 1
}
```

В ответе возвращаются текст ответа бота, идентификатор диалога и идентификатор следующего шага сценария.

## Тестирование

Для запуска автоматических тестов:

```bash
python manage.py test
```

Тесты проверяют CRUD-операции для ботов, сценариев и шагов, а также работу чата, обработку ошибок и переходы между шагами диалога.