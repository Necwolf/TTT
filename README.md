# TallyToTG

## Быстрый старт

1. Скопируйте файл `.env.example` в `.env` и укажите ваш Telegram Bot Token:

```
TELEGRAM_TOKEN=your-telegram-bot-token-here
```

2. Установите зависимости:

```
pip install -r requirements.txt
```

3. Запустите приложение:

```
python main.py
```

## Описание

Проект интегрирует Telegram-бота с вебхуками (например, от Tally), обрабатывает данные о командировках, формирует PDF-отчеты и отправляет их пользователю через Telegram.

## Переменные окружения

- `TELEGRAM_TOKEN` — токен вашего Telegram-бота (обязательно).

## Пример .env.example

```
TELEGRAM_TOKEN=your-telegram-bot-token-here
```

## API

### Эндпоинты

- `POST /{TELEGRAM_TOKEN}` — Webhook для Telegram-бота (aiogram)
- `POST /tally-webhook` — Прием данных от Tally (ожидает JSON, валидируется через Pydantic)
- `POST /tally-webhook-trip` — Прием данных о командировке (ожидает JSON, валидируется через Pydantic)
- `GET|POST /up` — Проверка статуса API
- `GET /` — Сброс и установка Telegram webhook

### Callback-кнопки Telegram-бота

- 📥 Підтвердити — подтверждение командировки
- 📄 PDF (детальний) — генерация детального PDF-отчета
- 📄 PDF (простий) — генерация простого PDF-отчета
- 📤 Надіслати email — подготовка PDF для отправки на email

## Тесты

- Для запуска тестов:

```
python -m unittest discover tests
``` 