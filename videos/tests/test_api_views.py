from django.urls import reverse
from rest_framework import status


class TestVideoListAPIView:
    """Тесты для API видео с django-filter"""

    def test_api_video_list_unauthenticated(self, api_client):
        """Неавторизованный доступ запрещён"""

        url = reverse("api_video_list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_api_video_list_authenticated(self, api_client, student_user, video):
        """Авторизованный пользователь получает список"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_video_list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_api_video_filter_by_level(self, api_client, student_user, video, intermediate_video):
        """Фильтрация по уровню через django-filter"""

        api_client.force_authenticate(user=student_user)
        url = reverse("api_video_list") + "?level=beginner"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert all(item["level"] == "beginner" for item in response.data)
