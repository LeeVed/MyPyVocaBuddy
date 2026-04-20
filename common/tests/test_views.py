from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class TestHomeView:
    """Тесты для home view"""

    def test_home_page_accessible(self, client):
        """Главная страница доступна всем"""

        url = reverse("common:home")
        response = client.get(url)
        assert response.status_code == 200
        assert "common/home.html" in [t.name for t in response.templates]

    def test_home_page_unauthenticated(self, client):
        """Неавторизованный пользователь видит кнопки входа/регистрации"""

        response = client.get(reverse("common:home"))
        content = response.content.decode()
        assert "Войти" in content or "Login" in content


class TestDashboardView:
    """Тесты для dashboard view"""

    def test_dashboard_requires_login(self, client):
        """Дашборд требует авторизации"""

        url = reverse("common:dashboard")
        response = client.get(url)
        assert response.status_code == 302

    def test_student_can_access_dashboard(self, client, student_user):
        """Студент может получить доступ к дашборду"""

        client.force_login(student_user)
        url = reverse("common:dashboard")
        response = client.get(url)
        assert response.status_code == 200

    def test_moderator_redirected_to_admin(self, client, moderator_user):
        """Модератор перенаправляется в админку"""

        client.force_login(moderator_user)
        url = reverse("common:dashboard")
        response = client.get(url)
        assert response.status_code == 302
        assert "/admin/" in response.url

    def test_admin_redirected_to_admin(self, client, admin_user):
        """Администратор перенаправляется в админку"""

        client.force_login(admin_user)
        url = reverse("common:dashboard")
        response = client.get(url)
        assert response.status_code == 302
        assert "/admin/" in response.url

    def test_dashboard_shows_statistics(self, client, student_user, user_words_batch):
        """Дашборд показывает корректную статистику"""

        client.force_login(student_user)
        response = client.get(reverse("common:dashboard"))

        assert response.status_code == 200
        assert response.context["total_words"] == 5
        assert "new_words" in response.context
        assert "to_review" in response.context
        assert "learned_words" in response.context
        assert "categories" in response.context

    def test_dashboard_with_category_filter(self, client, student_user, category):
        """Дашборд фильтрует слова по категории"""

        client.force_login(student_user)
        url = reverse("common:dashboard") + f"?category={category.slug}"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["selected_category_slug"] == category.slug
        assert response.context["selected_category_name"] == category.name

    def test_dashboard_with_invalid_category(self, client, student_user):
        """Дашборд обрабатывает несуществующую категорию"""

        client.force_login(student_user)
        url = reverse("common:dashboard") + "?category=nonexistent"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["selected_category_slug"] == "nonexistent"
        assert response.context["selected_category_name"] is None


class TestReviewView:
    """Тесты для review view"""

    def test_review_requires_login(self, client):
        """Повторение требует авторизации"""

        url = reverse("common:review")
        response = client.get(url)
        assert response.status_code == 302

    def test_student_can_access_review(self, client, student_user):
        """Студент может получить доступ к повторению (пустая сессия)"""

        client.force_login(student_user)
        response = client.get(reverse("common:review"))
        assert response.status_code == 200
        assert "common/review_empty.html" in [t.name for t in response.templates]

    def test_review_with_words(self, client, student_user, user_words_batch):
        """Повторение с доступными словами"""

        for uw in user_words_batch:
            uw.next_review_date = timezone.now() - timedelta(days=1)
            uw.save()

        client.force_login(student_user)
        response = client.get(reverse("common:review"))

        assert response.status_code == 200
        assert "common/review.html" in [t.name for t in response.templates]
        assert response.context["total_count"] <= 3  # лимит сессии

    def test_moderator_redirected(self, client, moderator_user):
        """Модератор перенаправляется в админку"""

        client.force_login(moderator_user)
        response = client.get(reverse("common:review"))
        assert response.status_code == 302
        assert "/admin/" in response.url


class TestWordListView:
    """Тесты для word_list view"""

    def test_word_list_requires_login(self, client):
        """Список слов требует авторизации"""

        url = reverse("common:word_list")
        response = client.get(url)
        assert response.status_code == 302

    def test_student_can_access_word_list(self, client, student_user):
        """Студент может получить доступ к списку слов"""

        client.force_login(student_user)
        response = client.get(reverse("common:word_list"))
        assert response.status_code == 200

    def test_word_list_with_status_filter(self, client, student_user, user_word, learned_user_word):
        """Список слов с фильтром по статусу"""

        client.force_login(student_user)
        url = reverse("common:word_list") + "?status=new"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["filter_status"] == "new"

    def test_word_list_with_category_filter(self, client, student_user, category):
        """Список слов с фильтром по категории"""

        client.force_login(student_user)
        url = reverse("common:word_list") + f"?category={category.slug}"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["selected_category_slug"] == category.slug

    def test_word_list_statistics(self, client, student_user, user_words_batch):
        """Список слов показывает корректную статистику"""

        client.force_login(student_user)
        response = client.get(reverse("common:word_list"))

        assert response.status_code == 200
        assert "total_count" in response.context
        assert "new_count" in response.context
        assert "review_count" in response.context
        assert "learned_count" in response.context
        assert "hidden_count" in response.context

    def test_moderator_redirected(self, client, moderator_user):
        """Модератор перенаправляется в админку"""

        client.force_login(moderator_user)
        response = client.get(reverse("common:word_list"))
        assert response.status_code == 302
        assert "/admin/" in response.url


class TestAddCustomWordView:
    """Тесты для add_custom_word view"""

    def test_add_custom_word_requires_login(self, client):
        """Добавление своего слова требует авторизации"""

        url = reverse("common:add_custom_word")
        response = client.get(url)
        assert response.status_code == 302

    def test_free_user_redirected(self, client, student_user):
        """Обычный пользователь перенаправляется"""

        client.force_login(student_user)
        url = reverse("common:add_custom_word")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("common:dashboard")

    def test_premium_user_can_access(self, client, premium_user):
        """Premium пользователь может получить доступ"""

        client.force_login(premium_user)
        url = reverse("common:add_custom_word")
        response = client.get(url)

        assert response.status_code == 200
        assert "common/add_custom_word.html" in [t.name for t in response.templates]

    def test_premium_user_can_add_word(self, client, premium_user, valid_custom_word_data):
        """Premium пользователь может добавить своё слово"""

        client.force_login(premium_user)
        url = reverse("common:add_custom_word")

        from vocabulary.models import UserWord
        initial_count = UserWord.objects.filter(user=premium_user).count()

        response = client.post(url, valid_custom_word_data)

        # Успешное добавление → редирект
        assert response.status_code == 302
        assert response.url == reverse("common:word_list")

        # Проверяем, что слово создалось
        assert UserWord.objects.filter(user=premium_user).count() == initial_count + 1

        # Проверяем, что слово создано с правильными данными
        new_word = UserWord.objects.filter(user=premium_user).latest("id")
        assert new_word.custom_term == "list_comprehension"
        assert new_word.custom_description == "Concise way to create lists in Python"

    def test_moderator_redirected(self, client, moderator_user):
        """Модератор перенаправляется в админку"""

        client.force_login(moderator_user)
        response = client.get(reverse("common:add_custom_word"))
        assert response.status_code == 302
        assert "/admin/" in response.url


class TestPremiumInfoView:
    """Тесты для premium_info view"""

    def test_premium_info_requires_login(self, client):
        """Страница Premium требует авторизации"""

        url = reverse("common:premium_info")
        response = client.get(url)
        assert response.status_code == 302

    def test_student_can_access(self, client, student_user):
        """Студент может получить доступ"""

        client.force_login(student_user)
        response = client.get(reverse("common:premium_info"))
        assert response.status_code == 200
        assert "premium/info.html" in [t.name for t in response.templates]

    def test_moderator_redirected(self, client, moderator_user):
        """Модератор перенаправляется в админку"""

        client.force_login(moderator_user)
        response = client.get(reverse("common:premium_info"))
        assert response.status_code == 302
        assert "/admin/" in response.url
