"""Фикстуры для тестов приложения users."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import Client
from vocabulary.models import Category, Word

User = get_user_model()


@pytest.fixture
def api_client():
    """API клиент"""
    return APIClient()


@pytest.fixture
def client():
    """Обычный Django клиент"""
    return Client()


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
        subscription_type="premium",
        language_level="intermediate"
    )


@pytest.fixture
def moderator_user(db):
    """Модератор"""

    return User.objects.create_user(
        username="moderator",
        email="moderator@test.com",
        password="testpass123",
        role="moderator",
        is_staff = True
    )


@pytest.fixture
def admin_user(db):
    """Администратор"""
    return User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="testpass123",
        role="admin",
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def valid_registration_data():
    """Валидные данные для регистрации"""
    return {
        "username": "newuser",
        "email": "newuser@test.com",
        "first_name": "John",
        "last_name": "Doe",
        "password1": "TestPass123!",
        "password2": "TestPass123!"
    }


@pytest.fixture
def invalid_registration_data():
    """Невалидные данные (пароли не совпадают)"""
    return {
        "username": "newuser",
        "email": "newuser@test.com",
        "password1": "TestPass123!",
        "password2": "WrongPass123!"
    }


@pytest.fixture
def fcm_device_data():
    """Данные для регистрации FCM устройства"""
    return {
        "token": "test_fcm_token_12345",
        "type": "web"
    }


@pytest.fixture
def category(db):
    """Категория для слов"""
    return Category.objects.create(
        name="Test Category",
        slug="test-category",
        description="Test description"
    )


@pytest.fixture
def word(db, category):
    """Слово"""
    return Word.objects.create(
        term="test_word",
        translation_description="Test description",
        category=category,
        difficulty=1
    )
