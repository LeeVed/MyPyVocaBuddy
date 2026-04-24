"""Фикстуры для тестов приложения vocabulary."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from vocabulary.models import Category, Word, UserWord

User = get_user_model()


@pytest.fixture
def student_user(db):
    """Обычный студент"""

    return User.objects.create_user(
        username="teststudent",
        email="student@test.com",
        password="testpass123",
        role="student",
        subscription_type="free"
    )


@pytest.fixture
def premium_user(db):
    """Premium студент"""

    return User.objects.create_user(
        username="premiumuser",
        email="premium@test.com",
        password="testpass123",
        role="student",
        subscription_type="premium"
    )


@pytest.fixture
def category(db):
    """Категория для слов"""

    return Category.objects.create(
        name="Python Basics",
        slug="python-basics",
        description="Basic Python concepts"
    )


@pytest.fixture
def second_category(db):
    """Вторая категория"""

    return Category.objects.create(
        name="Advanced Python",
        slug="advanced-python",
        description="Advanced concepts"
    )


@pytest.fixture
def word(db, category):
    """Слово из глобального словаря"""

    return Word.objects.create(
        term="variable",
        transcription="ˈverēəbəl",
        translation_description="Переменная — именованная область памяти",
        category=category,
        difficulty=1
    )


@pytest.fixture
def second_word(db, second_category):
    """Второе слово"""

    return Word.objects.create(
        term="function",
        transcription="ˈfəNG(k)SHən",
        translation_description="Функция — блок кода для многократного использования",
        category=second_category,
        difficulty=2
    )


@pytest.fixture
def inactive_word(db, category):
    """Неактивное слово"""

    return Word.objects.create(
        term="deprecated",
        translation_description="Устаревший термин",
        category=category,
        difficulty=1,
        is_active=False
    )


@pytest.fixture
def user_word(db, student_user, word):
    """Слово пользователя (новое)"""

    return UserWord.objects.create(
        user=student_user,
        word=word,
        stage=0,
        next_review_date=timezone.now() - timedelta(days=1),
        times_reviewed=0
    )


@pytest.fixture
def learned_user_word(db, student_user, second_word):
    """Выученное слово (stage=5)"""

    return UserWord.objects.create(
        user=student_user,
        word=second_word,
        stage=5,
        next_review_date=timezone.now() + timedelta(days=30),
        times_reviewed=10,
        is_learned=True
    )


@pytest.fixture
def hidden_user_word(db, premium_user, word):
    """Скрытое слово (Premium)"""

    return UserWord.objects.create(
        user=premium_user,
        word=word,
        stage=2,
        is_deleted_by_user=True
    )


@pytest.fixture
def custom_user_word(db, premium_user):
    """Пользовательское слово (без связи с Word)"""

    return UserWord.objects.create(
        user=premium_user,
        custom_term="list_comprehension",
        custom_transcription="lɪst ˌkɑmprɪˈhɛnʃən",
        custom_description="Генератор списков в Python",
        stage=0
    )


@pytest.fixture
def review_session_words(db, student_user, category):
    """Набор слов для сессии повторения"""

    words = []
    for i in range(3):
        w = Word.objects.create(
            term=f"review_word_{i}",
            translation_description=f"Description {i}",
            category=category,
            difficulty=1
        )
        uw = UserWord.objects.create(
            user=student_user,
            word=w,
            stage=0,
            next_review_date=timezone.now() - timedelta(days=1),
            times_reviewed=i
        )
        words.append(uw)
    return words


@pytest.fixture
def valid_custom_word_data():
    """Валидные данные для формы CustomWordForm"""

    return {
        "term": "decorator",
        "transcription": "ˈdekəˌrādər",
        "description": "Декоратор — функция, модифицирующая поведение другой функции"
    }


@pytest.fixture
def invalid_custom_word_data():
    """Невалидные данные для формы"""

    return {
        "term": "",  # Пустое поле
        "description": "No term"
    }
