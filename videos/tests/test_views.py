from django.urls import reverse
from vocabulary.models import UserWord
import json


class TestVideoListView:
    """Тесты для video_list view"""

    def test_video_list_requires_login(self, client):
        """Список видео требует авторизации"""

        url = reverse("videos:list")
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_student_can_access_video_list(self, client, student_user, video):
        """Студент может получить доступ к списку видео"""

        client.force_login(student_user)
        url = reverse("videos:list")
        response = client.get(url)

        assert response.status_code == 200
        assert "videos/list.html" in [t.name for t in response.templates]
        assert video in response.context["videos"]

    def test_premium_user_can_filter_by_level(self, client, premium_user, video, intermediate_video):
        """Premium пользователь может фильтровать видео по уровню"""

        client.force_login(premium_user)
        url = reverse("videos:list") + "?level=beginner"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["level_filter"] == "beginner"
        assert video in response.context["videos"]
        assert intermediate_video not in response.context["videos"]

    def test_free_user_cannot_filter_by_level(self, client, student_user, video, intermediate_video):
        """Free пользователь не может фильтровать (фильтр игнорируется)"""

        client.force_login(student_user)
        url = reverse("videos:list") + "?level=beginner"
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["level_filter"] is None
        # Все видео отображаются
        assert video in response.context["videos"]
        assert intermediate_video in response.context["videos"]

    def test_inactive_videos_not_shown(self, client, student_user, inactive_video, video):
        """Неактивные видео не отображаются в списке"""

        client.force_login(student_user)
        url = reverse("videos:list")
        response = client.get(url)

        assert video in response.context["videos"]
        assert inactive_video not in response.context["videos"]

    def test_moderator_can_access(self, client, moderator_user, video):
        """Модератор может получить доступ"""

        client.force_login(moderator_user)
        url = reverse("videos:list")
        response = client.get(url)
        assert response.status_code == 200


class TestVideoDetailView:
    """Тесты для video_detail view"""

    def test_video_detail_requires_login(self, client, video):
        """Детальная страница требует авторизации"""

        url = reverse("videos:detail", kwargs={"pk": video.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_student_can_view_video(self, client, student_user, video):
        """Студент может смотреть видео"""
        client.force_login(student_user)
        url = reverse("videos:detail", kwargs={"pk": video.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert "videos/detail.html" in [t.name for t in response.templates]
        assert response.context["video"] == video

    def test_free_user_can_view_premium_video(self, client, student_user, premium_video):
        """Free пользователь может смотреть Premium видео (но без доп. функций)"""

        client.force_login(student_user)
        url = reverse("videos:detail", kwargs={"pk": premium_video.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["is_premium_user"] is False

    def test_premium_user_sees_premium_flag(self, client, premium_user, premium_video):
        """Premium пользователь видит флаг is_premium_user=True"""

        client.force_login(premium_user)
        url = reverse("videos:detail", kwargs={"pk": premium_video.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["is_premium_user"] is True

    def test_404_for_inactive_video(self, client, student_user, inactive_video):
        """Неактивное видео возвращает 404"""

        client.force_login(student_user)
        url = reverse("videos:detail", kwargs={"pk": inactive_video.pk})
        response = client.get(url)
        assert response.status_code == 404

    def test_404_for_nonexistent_video(self, client, student_user):
        """Несуществующее видео возвращает 404"""

        client.force_login(student_user)
        url = reverse("videos:detail", kwargs={"pk": 99999})
        response = client.get(url)
        assert response.status_code == 404


class TestAddWordsView:
    """Тесты для add_words view"""

    def test_add_words_requires_login(self, client, video):
        """Добавление слов требует авторизации"""

        url = reverse("videos:add_words", kwargs={"pk": video.pk})
        response = client.post(url)
        assert response.status_code == 302

    def test_add_words_requires_post(self, client, premium_user, video):
        """Только POST запросы разрешены"""

        client.force_login(premium_user)
        url = reverse("videos:add_words", kwargs={"pk": video.pk})
        response = client.get(url)
        assert response.status_code == 405

    def test_premium_user_can_add_words(self, client, premium_user, video, word, second_word):
        """Premium пользователь может добавить слова из видео"""

        client.force_login(premium_user)
        url = reverse("videos:add_words", kwargs={"pk": video.pk})

        initial_count = UserWord.objects.filter(user=premium_user).count()

        response = client.post(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert "Добавлено 2 новых слов" in data["message"]

        assert UserWord.objects.filter(user=premium_user).count() == initial_count + 2

    def test_free_user_cannot_add_words(self, client, student_user, video):
        """Free пользователь не может добавлять слова"""

        client.force_login(student_user)
        url = reverse("videos:add_words", kwargs={"pk": video.pk})

        response = client.post(url)

        assert response.status_code == 403
        data = json.loads(response.content)
        assert "Premium" in data["error"]

    def test_moderator_cannot_add_words(self, client, moderator_user, video):
        """Модератор не может добавлять слова"""

        client.force_login(moderator_user)
        url = reverse("videos:add_words", kwargs={"pk": video.pk})

        response = client.post(url)

        assert response.status_code == 403
        data = json.loads(response.content)
        assert "запрещён" in data["error"]

    def test_add_words_no_duplicates(self, client, premium_user, video, word):
        """Слова не дублируются при повторном добавлении"""

        client.force_login(premium_user)
        url = reverse("videos:add_words", kwargs={"pk": video.pk})

        # Первый раз
        client.post(url)
        first_count = UserWord.objects.filter(user=premium_user).count()

        # Второй раз
        response = client.post(url)
        data = json.loads(response.content)

        assert data["success"] is True
        assert "Добавлено 0 новых слов" in data["message"]
        assert UserWord.objects.filter(user=premium_user).count() == first_count

    def test_add_words_video_not_found(self, client, premium_user):
        """Обработка несуществующего видео"""

        client.force_login(premium_user)
        url = reverse("videos:add_words", kwargs={"pk": 99999})
        response = client.post(url)
        assert response.status_code == 404

    def test_add_words_inactive_video(self, client, premium_user, inactive_video):
        """Нельзя добавить слова из неактивного видео"""

        client.force_login(premium_user)
        url = reverse("videos:add_words", kwargs={"pk": inactive_video.pk})
        response = client.post(url)
        assert response.status_code == 404
