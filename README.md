# 🐍 MyPyVocaBuddy

**MyPyVocaBuddy** — веб-приложение в версиях ru/en для изучения терминов Python с использованием системы интервальных повторений (SRS) 
и видео-имитации произношения (техника shadowing).

Дипломный проект по специальности «Python-разработчик».

---

## 🚀 Функциональность

### 👤 Для студентов (Free)
- 📚 Изучение базовых терминов Python
- 🔄 Повторение слов по системе SRS (интервальные повторения)
- ✏️ Три режима проверки: **Показать**, **Написать**, **Произнести**
- 🎬 Просмотр видео из видеотеки
- 🌐 Двуязычный интерфейс (русский / английский)

### ⭐ Для Premium-пользователей
- ➕ Добавление **своих слов** с изображениями
- 🎯 Фильтрация видео по уровню сложности
- 📊 Расширенная статистика произношения
- 🗑️ Скрытие/восстановление слов

### 🛠️ Для администраторов
- Управление пользователями
- Управление словарём и категориями
- Управление видеотекой

---

## 🧱 Технологический стек

| Категория | Технологии |
|---|---|
| **Backend** | Django 4.2, Django REST Framework |
| **База данных** | PostgreSQL |
| **Очереди** | Celery + Redis |
| **Уведомления** | Firebase Cloud Messaging (FCM) |
| **Контейнеризация** | Docker, Docker Compose |
| **Веб-сервер** | Nginx |
| **Тестирование** | pytest, pytest-django, pytest-cov |
| **CI/CD** | GitHub Actions |
| **Деплой** | Яндекс.Облако |

---

## 📦 Установка и запуск (локально)

### 1. Клонировать репозиторий

git clone https://github.com/your-username/MyPyVocaBuddy.git
cd MyPyVocaBuddy

### 2. Установить зависимости

pip install poetry
poetry install

### 3. Настроить переменные окружения

cp .env.sample .env
# Отредактировать .env — указать SECRET_KEY, настройки БД

### 4. Применить миграции

poetry run python manage.py migrate

### 5. Запустить сервер

poetry run python manage.py runserver

Открыть: http://127.0.0.1:8000

---

## 🐳 Запуск в Docker

docker-compose up -d --build

Открыть: http://localhost

---

## 🧪 Тестирование

poetry run pytest -v
poetry run pytest --cov=. --cov-report=html

**Покрытие тестами:** >85% (203+ тестов)

---

## 📁 Структура проекта

MyPyVocaBuddy/
├── common/                 # Основной функционал
├── users/                  # Пользователи, регистрация
├── vocabulary/             # Слова и SRS-логика
├── videos/                 # Видеотека
├── premium/                # Premium-функционал 
├── config/                 # Настройки Django
├── locale/                 # Переводы
├── nginx/                  # Конфиг Nginx
├── .github/workflows/      # CI/CD
├── Dockerfile
├── docker-compose.yml
└── README.md

---

## 👨‍💻 Автор

**Веденеева Лидия**
Дипломный проект, 2026

---

## 📄 Лицензия

MIT License
