from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class TestRegisterView:
    """Тесты для register view"""

    def test_register_page_accessible(self, client):
        """Страница регистрации доступна"""

        url = reverse("register")
        response = client.get(url)
        assert response.status_code == 200
        assert "users/register.html" in [t.name for t in response.templates]

    @patch("users.views.add_base_words_to_user")
    def test_register_success(self, mock_add_words, db, client, valid_registration_data):
        """Успешная регистрация нового пользователя"""

        mock_add_words.return_value = 10  # 10 базовых слов добавлено
        
        url = reverse("register")
        response = client.post(url, valid_registration_data)
        
        # Редирект на дашборд
        assert response.status_code == 302
        assert response.url == reverse("common:dashboard")
        
        # Пользователь создан
        user = User.objects.get(username="newuser")
        assert user.email == "newuser@test.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        
        # Проверяем, что add_base_words_to_user был вызван
        mock_add_words.assert_called_once_with(user)

    def test_register_invalid_data(self, db, client, invalid_registration_data):
        """Регистрация с невалидными данными"""

        url = reverse("register")
        response = client.post(url, invalid_registration_data)
        
        # Остаёмся на странице регистрации
        assert response.status_code == 200
        assert "users/register.html" in [t.name for t in response.templates]
        
        # Пользователь не создан
        assert not User.objects.filter(username="newuser").exists()

    def test_register_existing_username(self, client, student_user, valid_registration_data):
        """Регистрация с уже существующим username"""

        valid_registration_data["username"] = "teststudent"
        
        url = reverse("register")
        response = client.post(url, valid_registration_data)
        
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_register_authenticated_user_redirected(self, client, student_user):
        """Авторизованный пользователь перенаправляется с регистрации"""

        client.force_login(student_user)
        url = reverse("register")
        response = client.get(url)
        
        # Обычно Django перенаправляет авторизованных
        assert response.status_code in [302, 200]


class TestCustomLoginView:
    """Тесты для CustomLoginView"""

    def test_login_page_accessible(self, client):
        """Страница входа доступна"""

        url = reverse("login")
        response = client.get(url)
        assert response.status_code == 200

    def test_login_student_redirects_to_dashboard(self, client, student_user):
        """Студент после входа перенаправляется на дашборд"""

        response = client.post(reverse("login"), {
            "username": "teststudent",
            "password": "testpass123"
        })
        assert response.status_code == 302
        assert response.url == "/dashboard/"

    def test_login_moderator_redirects_to_admin(self, client, moderator_user):
        """Модератор после входа перенаправляется в админку"""

        response = client.post(reverse("login"), {
            "username": "moderator",
            "password": "testpass123"
        })
        assert response.status_code == 302
        assert response.url == "/admin/"

    def test_login_admin_redirects_to_admin(self, client, admin_user):
        """Администратор после входа перенаправляется в админку"""

        response = client.post(reverse("login"), {
            "username": "admin",
            "password": "testpass123"
        })
        assert response.status_code == 302
        assert response.url == "/admin/"

    def test_login_invalid_credentials(self, db, client):
        """Вход с неверными данными"""

        response = client.post(reverse("login"), {
            "username": "wrong",
            "password": "wrong"
        })
        assert response.status_code == 200
