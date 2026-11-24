# Конструктор GPT-ботов

Учебный проект на **Python, Django и Django REST Framework** для создания GPT-ботов, настройки сценариев общения и обработки сообщений пользователей.

## Демо

**Работающее приложение:** https://bot-constructor.de3.netrun.io

**GitHub:** https://github.com/mrrago7/bot-constructor

## Возможности

- Создание, просмотр, изменение и удаление ботов (CRUD).
- Создание и управление сценариями общения.
- Создание и управление шагами сценариев.
- Связывание шагов для построения последовательного диалога.
- Обработка сообщений через GPT API.
- Сохранение состояния диалога между сообщениями.
- Управление данными через Django Admin.
- Автоматические API-тесты.

## Технологии

- Python 3.12
- Django 6.1
- Django REST Framework
- OpenAI API
- PostgreSQL
- SQLite (для локальной разработки без PostgreSQL)
- Gunicorn
- Nginx
- Docker и Docker Compose
- GitHub Actions
- GitHub Container Registry (GHCR)
- pip-tools

## Структура проекта

```text
bot-constructor/
├── api/                    # API, модели, сериализаторы и тесты
├── config/                 # Настройки Django и маршрутизация
├── nginx/                  # Конфигурация Nginx
├── .github/
│   └── workflows/          # GitHub Actions
├── Dockerfile              # Сборка Docker-образа
├── docker-compose.yml      # Запуск контейнеров
├── requirements.in         # Основные зависимости
├── requirements.txt        # Зафиксированные зависимости
├── manage.py
└── README.md
```

## Установка и локальный запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/mrrago7/bot-constructor.git
cd bot-constructor
```

### 2. Создание виртуального окружения

```bash
python -m venv .venv
```

Активация в Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей

```bash
python -m pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt
```

### 4. Настройка переменных окружения

Создать в корне проекта файл `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=
```

Для локального запуска без PostgreSQL используется SQLite.

### 5. Миграции и запуск

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После запуска:

- API: http://127.0.0.1:8000/api/
- Панель администратора: http://127.0.0.1:8000/admin/

## Запуск через Docker

Для запуска контейнеров необходимо установить Docker Desktop.

В корне проекта создать файл `.env` и указать переменные:

```env
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_PASSWORD=your-database-password
OPENAI_API_KEY=
```

Запустить приложение:

```bash
docker compose up -d --build
```

Остановить контейнеры:

```bash
docker compose down
```

В Docker Compose используются три сервиса:

- **web** — Django-приложение с Gunicorn;
- **db** — PostgreSQL;
- **nginx** — веб-сервер и проксирование запросов.

Данные PostgreSQL и собранные статические файлы хранятся в Docker volumes.

## Настройка GPT

По умолчанию проект работает в тестовом режиме (`OPENAI_MOCK_MODE = True`). В этом режиме возвращаются тестовые ответы, поэтому API-ключ OpenAI не требуется.

Для использования реального OpenAI API необходимо отключить тестовый режим в настройках проекта и указать действующий API-ключ через переменную окружения `OPENAI_API_KEY`.

## API

Базовый адрес API:

```text
/api/
```

### Боты

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/bots/` | Получить список ботов |
| POST | `/api/bots/` | Создать бота |
| GET | `/api/bots/{id}/` | Получить бота |
| PUT | `/api/bots/{id}/` | Обновить бота |
| DELETE | `/api/bots/{id}/` | Удалить бота |

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

Для управления шагами доступны вложенные маршруты:

```text
/api/scenarios/{id}/steps/
/api/scenarios/{id}/steps/{step_id}/
```

Также доступен отдельный CRUD для шагов:

```text
/api/steps/
```

### Общение с ботом

Отправка сообщения:

```http
POST /api/bots/{id}/chat/
```

Пример тела запроса:

```json
{
    "message": "Привет!"
}
```

Для продолжения существующего диалога передаётся `conversation_id`:

```json
{
    "message": "Продолжим",
    "conversation_id": 1
}
```

## Тестирование

Запуск автоматических тестов:

```bash
python manage.py test
```

Тесты проверяют CRUD-операции для ботов, сценариев и шагов, а также работу чата, обработку ошибок и переходы между шагами диалога.

## CI/CD

В проекте настроен GitHub Actions.

При отправке изменений в ветку `master` автоматически:

1. Загружается исходный код репозитория.
2. Настраивается Docker Buildx.
3. Выполняется вход в GitHub Container Registry.
4. Собирается Docker-образ приложения.
5. Образ публикуется в GHCR с тегами `latest` и идентификатором коммита.

Workflow находится в `.github/workflows/docker.yml`.

## Развёртывание

Приложение развёрнуто на платформе Netrun с использованием Docker Compose.

**Публичная ссылка:** https://bot-constructor.de3.netrun.io

В развёрнутом приложении используются Django, PostgreSQL и Nginx.

---

Учебный проект.