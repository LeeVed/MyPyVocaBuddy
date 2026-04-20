import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCustomUser:
    """Тесты для CustomUser"""

    def test_create_user(self, db):
        """Создание обычного пользователя"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "student"  # по умолчанию
        assert user.subscription_type == "free"  # по умолчанию
        assert user.preferred_language == "ru"  # по умолчанию
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self, db):
        """Создание суперпользователя"""
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_user_str_representation(self, student_user):
        """Строковое представление пользователя"""
        assert str(student_user) == "teststudent (Free)"

    def test_user_str_premium(self, premium_user):
        """Строковое представление Premium пользователя"""
        assert str(premium_user) == "premiumuser (Premium)"

    def test_can_set_language_level_free(self, student_user):
        """Free пользователь не может установить уровень языка"""
        assert student_user.can_set_language_level is False

    def test_can_set_language_level_premium(self, premium_user):
        """Premium пользователь может установить уровень языка"""
        assert premium_user.can_set_language_level is True

    def test_language_level_validation_free_user(self, db):
        """Free пользователь не может сохранить language_level"""
        user = User.objects.create_user(
            username="freeuser",
            password="testpass123",
            subscription_type="free",
            language_level="beginner"  # пытаемся установить
        )
        with pytest.raises(ValidationError):
            user.clean()

    def test_language_level_validation_premium_user(self, db):
        """Premium пользователь может сохранить language_level"""
        user = User.objects.create_user(
            username="premiumuser2",
            password="testpass123",
            subscription_type="premium",
            language_level="intermediate"
        )
        # Не должно вызывать ошибку
        user.clean()

    def test_save_resets_language_level_on_downgrade(self, premium_user):
        """При смене подписки с premium на free language_level сбрасывается"""
        assert premium_user.language_level == "intermediate"

        premium_user.subscription_type = "free"
        premium_user.save()
        premium_user.refresh_from_db()

        assert premium_user.language_level is None

    def test_get_avatar_url_default(self, student_user):
        """URL аватара по умолчанию"""
        assert student_user.get_avatar_url == "/static/images/default-avatar.png"

    def test_preferred_language_default(self, db):
        """Язык интерфейса по умолчанию — русский"""
        user = User.objects.create_user(username="test", password="test")
        assert user.preferred_language == "ru"


class TestCustomUserProperties:
    """Тесты для свойств CustomUser"""

    def test_is_premium_property(self, premium_user, student_user):
        """Свойство is_premium (если определено)"""

        if hasattr(premium_user, 'is_premium'):
            assert premium_user.is_premium is True
            assert student_user.is_premium is False

    def test_full_name_property(self, db):
        """Полное имя пользователя"""
        user = User.objects.create_user(
            username="john",
            first_name="John",
            last_name="Doe"
        )
        assert user.get_full_name() == "John Doe"
