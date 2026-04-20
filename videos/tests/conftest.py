"""Фикстуры для тестов приложения videos."""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from videos.models import Video
from vocabulary.models import Category, Word
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """API клиент для тестирования DRF"""
    return APIClient()


@pytest.fixture
def client():
    """Обычный Django клиент"""

    return Client()


@pytest.fixture
def student_user(db):
    """Обычный студент (free)"""

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
def moderator_user(db):
    """Модератор"""

    return User.objects.create_user(
        username="moderator",
        email="moderator@test.com",
        password="testpass123",
        role="moderator",
        is_staff=True
    )


@pytest.fixture
def category(db):
    """Категория для слов"""

    return Category.objects.create(
        name="Python Basics",
        slug="python-basics"
    )


@pytest.fixture
def word(db, category):
    """Слово"""

    return Word.objects.create(
        term="variable",
        translation_description="Переменная",
        category=category,
        difficulty=1
    )


@pytest.fixture
def second_word(db, category):
    """Второе слово"""

    return Word.objects.create(
        term="function",
        translation_description="Функция",
        category=category,
        difficulty=2
    )


@pytest.fixture
def video(db, word, second_word):
    """Видео"""

    video = Video.objects.create(
        title="Python Variables Tutorial",
        youtube_url="https://www.youtube.com/watch?v=abc123",
        description="Learn about variables in Python",
        level="beginner",
        is_premium=False,
        duration=366  # 6:06
    )
    video.words.add(word, second_word)
    return video


@pytest.fixture
def premium_video(db, word):
    """Premium видео"""

    video = Video.objects.create(
        title="Advanced Python Decorators",
        youtube_url="https://youtu.be/xyz789",
        description="Deep dive into decorators",
        level="advanced",
        is_premium=True,
        duration=720  # 12:00
    )
    video.words.add(word)
    return video


@pytest.fixture
def inactive_video(db):
    """Неактивное видео"""

    return Video.objects.create(
        title="Deprecated Tutorial",
        youtube_url="https://www.youtube.com/watch?v=old123",
        level="beginner",
        is_active=False
    )


@pytest.fixture
def intermediate_video(db):
    """Видео среднего уровня"""

    return Video.objects.create(
        title="Python Functions",
        youtube_url="https://www.youtube.com/watch?v=def456",
        description="Functions in Python",
        level="intermediate",
        is_premium=False,
        duration=480  # 8:00
    )
