# recognize_speech_bot

Telegram и ВКонтакте боты с интеграцией DialogFlow для распознавания речи и ответов на вопросы.

## Описание

Проект состоит из двух ботов (Telegram и ВКонтакте), которые используют DialogFlow API для обработки естественного языка. Боты отвечают на вопросы пользователей по базе знаний, а непонятные вопросы передают операторам техподдержки.

## Структура проекта

- `telegram_bot.py` — бот для Telegram
- `vk_bot.py` — бот для ВКонтакте (с интеграцией DialogFlow)
- `add_intent.py` — скрипт для создания интентов в DialogFlow из JSON
- `learning_offers.json` — база знаний (вопросы и ответы)
- `requirements.txt` — зависимости проекта

## Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone <url-вашего-репозитория>
cd recognize_speech_bot
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Создайте файл .env

```env
TELEGRAM_TOKEN_BOT=ваш_токен_от_BotFather
GOOGLE_APPLICATION_CREDENTIALS=путь/к/credentials.json
GOOGLE_PROJECT_ID=ваш_project_id
VK_GROUP_TOKEN=ваш_токен_группы_ВК
VK_GROUP_ID=ваш_id_группы
```

### 5. Запуск ботов

```bash
python telegram_bot.py
```

### ВКонтакте:

```bash
python vk_bot.py
```

### 6. Создание интентов в DialogFlow

```bash
python add_intent.py
```

## Лицензия
MIT License. Подробнее в файле LICENSE.