"""
Фикстуры для тестов приложения common.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import Client
from django.utils import timezone
from datetime import timedelta

from vocabulary.models import UserWord, Word, Category

User = get_user_model()

# CLIENT FIXTURES
@pytest.fixture
def api_client():
    """
    Неавторизованный API клиент.

    Используется для тестирования эндпоинтов без аутентификации.
    """
    return APIClient()


@pytest.fixture
def client():
    """
    Обычный Django тестовый клиент.

    Используется для тестирования обычных views (не API).
    """
    return Client()

# USER FIXTURES
@pytest.fixture
def student_user(db):
    """
    Обычный студент (free подписка).

    Имеет доступ к базовому функционалу:
    - Дашборд
    - Повторение слов
    - Просмотр видео (без фильтрации)
    - НЕ может добавлять свои слова
    - НЕ может скрывать/восстанавливать слова
    """
    return User.objects.create_user(
        username="student",
        email="student@example.com",
        password="testpass123",
        role="student",
        subscription_type="free"
    )


@pytest.fixture
def premium_user(db):
    """
    Premium студент.

    Имеет доступ ко всем функциям:
    - Всё что есть у обычного студента
    - Фильтрация видео по уровню
    - Добавление своих слов
    - Скрытие/восстановление слов
    - Генерация изображений через ИИ
    """
    return User.objects.create_user(
        username="premium",
        email="premium@example.com",
        password="testpass123",
        role="student",
        subscription_type="premium"
    )


@pytest.fixture
def moderator_user(db):
    """
    Модератор.

    Перенаправляется в админку при попытке доступа к пользовательским страницам.
    """
    return User.objects.create_user(
        username="moderator",
        email="moderator@example.com",
        password="testpass123",
        role="moderator"
    )


@pytest.fixture
def admin_user(db):
    """
    Администратор.

    Перенаправляется в админку при попытке доступа к пользовательским страницам.
    """
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="testpass123",
        role="admin",
        is_staff=True,
        is_superuser=True
    )

# AUTHENTICATED CLIENT FIXTURES
@pytest.fixture
def authenticated_api_client(api_client, student_user):
    """
    API клиент, авторизованный как обычный студент.

    Удобно когда нужно тестировать эндпоинты, требующие аутентификации.
    """
    api_client.force_authenticate(user=student_user)
    api_client.user = student_user
    return api_client


@pytest.fixture
def premium_api_client(api_client, premium_user):
    """
    API клиент, авторизованный как Premium студент.
    """
    api_client.force_authenticate(user=premium_user)
    api_client.user = premium_user
    return api_client


@pytest.fixture
def moderator_api_client(api_client, moderator_user):
    """
    API клиент, авторизованный как модератор.
    """
    api_client.force_authenticate(user=moderator_user)
    api_client.user = moderator_user
    return api_client


@pytest.fixture
def authenticated_client(client, student_user):
    """
    Обычный Django клиент, авторизованный как студент.
    """
    client.force_login(student_user)
    return client


@pytest.fixture
def premium_client(client, premium_user):
    """
    Обычный Django клиент, авторизованный как Premium студент.
    """
    client.force_login(premium_user)
    return client

# VOCABULARY FIXTURES
@pytest.fixture
def category(db):
    """
    Категория (тема) для слов.

    Используется при создании слов и фильтрации.
    """
    return Category.objects.create(
        name="Python Basics",
        slug="python-basics",
        description="Basic Python concepts for beginners"
    )


@pytest.fixture
def second_category(db):
    """
    Вторая категория для тестирования фильтрации.
    """
    return Category.objects.create(
        name="Advanced Python",
        slug="advanced-python",
        description="Advanced Python concepts"
    )


@pytest.fixture
def categories(db, category, second_category):
    """
    Список всех категорий.
    """
    return [category, second_category]


@pytest.fixture
def word(db, category):
    """Слово"""

    return Word.objects.create(
        term="variable",
        transcription="ˈverēəbəl",
        translation_description="A storage location paired with an associated symbolic name",
        category=category,
        difficulty=1
    )


@pytest.fixture
def advanced_word(db, second_category):
    """
    Слово из продвинутой категории.
    """
    return Word.objects.create(
        term="decorator",
        transcription="ˈdekəˌrādər",
        translation_description="A function that modifies the behavior of another function",
        category=second_category,
        difficulty=3
    )


@pytest.fixture
def user_word(db, student_user, word):
    """
    Слово, добавленное в словарь обычного студента.

    Статус: новое (stage=0), требует повторения (дата в прошлом).
    """
    return UserWord.objects.create(
        user=student_user,
        word=word,
        stage=0,
        times_reviewed=0,
        next_review_date=timezone.now() - timedelta(days=1)
    )


@pytest.fixture
def learned_user_word(db, student_user, word):
    """Выученное слово (stage >= 5)"""

    new_word = Word.objects.create(
        term="learned_variable",
        transcription="ˈlɜːnɪd",
        translation_description="A learned concept",
        category=word.category,
        difficulty=1
    )
    return UserWord.objects.create(
        user=student_user,
        word=new_word,
        stage=5,
        times_reviewed=10,
        next_review_date=timezone.now() + timedelta(days=30)
    )


@pytest.fixture
def hidden_user_word(db, student_user, word):
    """Скрытое слово"""

    new_word = Word.objects.create(
        term="hidden_variable",
        transcription="ˈhɪdən",
        translation_description="A hidden concept",
        category=word.category,
        difficulty=1
    )
    return UserWord.objects.create(
        user=student_user,
        word=new_word,
        stage=2,
        is_deleted_by_user=True
    )


@pytest.fixture
def custom_user_word(db, student_user):
    """
    Пользовательское слово (добавлено студентом, не из глобального словаря).

    Доступно только Premium пользователям.
    """
    return UserWord.objects.create(
        user=student_user,
        custom_term="my_custom_function",
        custom_transcription="maɪ ˈkʌstəm ˈfʌŋkʃən",
        custom_description="My own function definition",
        stage=0
    )


@pytest.fixture
def review_session(db, student_user, category):
    """
    Сессия повторения из 3 слов.

    Используется для тестирования процесса повторения.
    Все слова требуют повторения (next_review_date в прошлом).
    """
    words = []
    for i in range(3):
        w = Word.objects.create(
            term=f"test_word_{i}",
            transcription=f"test_tr_{i}",
            translation_description=f"Test description {i}",
            category=category,
            difficulty=1
        )
        uw = UserWord.objects.create(
            user=student_user,
            word=w,
            stage=0,
            times_reviewed=i,
            next_review_date=timezone.now() - timedelta(days=i + 1)
        )
        words.append(uw)
    return words


@pytest.fixture
def user_words_batch(db, student_user, category):
    """
    Набор из 5 слов пользователя с разными стадиями изучения.

    Стадии: 0, 1, 2, 3, 4
    Используется для тестирования статистики и фильтрации.
    """
    words = []
    for i in range(5):
        w = Word.objects.create(
            term=f"word_stage_{i}",
            translation_description=f"Description for stage {i}",
            category=category,
            difficulty=1
        )
        next_review = timezone.now() - timedelta(days=i) if i < 3 else timezone.now() + timedelta(days=i)
        uw = UserWord.objects.create(
            user=student_user,
            word=w,
            stage=i,
            times_reviewed=i * 2,
            next_review_date=next_review
        )
        words.append(uw)
    return words


@pytest.fixture
def premium_user_word(db, premium_user, word):
    """
    Слово, принадлежащее Premium пользователю.

    Используется для тестирования Premium-функций (скрытие, восстановление).
    """
    return UserWord.objects.create(
        user=premium_user,
        word=word,
        stage=0
    )

# REQUEST/SESSION FIXTURES
@pytest.fixture
def api_client_with_review_session(api_client, student_user, review_session):
    """
    API клиент с настроенной сессией повторения.

    В сессии уже есть очередь слов для повторения.
    """
    api_client.force_authenticate(user=student_user)
    session = api_client.session
    session["review_queue"] = [w.id for w in review_session]
    session["review_current_index"] = 0
    session["review_mode"] = "show"
    session.save()
    api_client.user = student_user
    return api_client


@pytest.fixture
def api_client_with_empty_session(api_client, student_user):
    """
    API клиент с пустой сессией повторения.

    Используется для тестирования завершения сессии.
    """
    api_client.force_authenticate(user=student_user)
    session = api_client.session
    session["review_queue"] = []
    session["review_current_index"] = 0
    session.save()
    api_client.user = student_user
    return api_client

# FORM DATA FIXTURES
@pytest.fixture
def valid_custom_word_data():
    """
    Валидные данные для формы добавления пользовательского слова.
    Поля должны соответствовать CustomWordForm.
    """
    return {
        "term": "list_comprehension",
        "transcription": "lɪst ˌkɑmprɪˈhɛnʃən",
        "description": "Concise way to create lists in Python",
    }


@pytest.fixture
def invalid_custom_word_data():
    """
    Невалидные данные для формы добавления пользовательского слова.
    """
    return {
        "term": "",
        "custom_description": "No term provided"
    }


@pytest.fixture
def profane_custom_word_data():
    """
    Данные с нецензурной лексикой.
    """
    return {
        "term": "fuck",
        "custom_description": "This contains profanity"
    }

# MOCK FIXTURES (для внешних сервисов)
@pytest.fixture
def mock_speech_recognition(mocker):
    """
    Мок для Web Speech API.

    Используется в тестах произношения, чтобы не зависеть от браузерного API.
    """
    mock_recognition = mocker.Mock()
    mock_recognition.lang = "en-US"
    return mock_recognition


@pytest.fixture
def mock_firebase(mocker):
    """
    Мок для Firebase (push-уведомления).
    """
    mock_firebase_app = mocker.patch("firebase_admin.initialize_app")
    mock_messaging = mocker.patch("firebase_admin.messaging")
    return {
        "app": mock_firebase_app,
        "messaging": mock_messaging
    }

# UTILITY FIXTURES
@pytest.fixture
def now():
    """
    Текущее время с учётом timezone.
    """
    return timezone.now()


@pytest.fixture
def yesterday(now):
    """
    Вчерашняя дата.
    """
    return now - timedelta(days=1)


@pytest.fixture
def tomorrow(now):
    """
    Завтрашняя дата.
    """
    return now + timedelta(days=1)


@pytest.fixture
def next_week(now):
    """
    Дата через неделю.
    """
    return now + timedelta(days=7)
