from users.forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCustomUserCreationForm:
    """Тесты для CustomUserCreationForm"""

    def test_form_valid_data(self, db, valid_registration_data):
        """Форма валидна с правильными данными"""

        form = CustomUserCreationForm(data=valid_registration_data)
        assert form.is_valid()

    def test_form_invalid_password_mismatch(self, db, invalid_registration_data):
        """Форма невалидна, если пароли не совпадают"""

        form = CustomUserCreationForm(data=invalid_registration_data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_form_empty_username(self, db):
        """Форма требует username"""

        data = {
            "username": "",
            "email": "test@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!"
        }
        form = CustomUserCreationForm(data=data)
        assert not form.is_valid()
        assert "username" in form.errors

    def test_form_empty_email(self, db):
        """Форма требует email"""

        data = {
            "username": "testuser",
            "email": "",
            "password1": "TestPass123!",
            "password2": "TestPass123!"
        }
        form = CustomUserCreationForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_form_save_creates_user(self, db, valid_registration_data):
        """Форма создаёт пользователя с правильными данными"""

        form = CustomUserCreationForm(data=valid_registration_data)
        assert form.is_valid()

        user = form.save()

        assert user.username == "newuser"
        assert user.email == "newuser@test.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.check_password("TestPass123!") is True

    def test_form_widget_attrs(self, db):
        """Проверка CSS-классов Bootstrap"""

        form = CustomUserCreationForm()

        assert form.fields["username"].widget.attrs["class"] == "form-control"
        assert form.fields["email"].widget.attrs["class"] == "form-control"
        assert form.fields["password1"].widget.attrs["class"] == "form-control"
        assert form.fields["password2"].widget.attrs["class"] == "form-control"

    def test_form_profanity_validation(self, db):
        """Форма невалидна при нецензурной лексике"""

        data = {
            "username": "fuck",
            "email": "test@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!"
        }
        form = CustomUserCreationForm(data=data)
        assert not form.is_valid()
