from django.urls import reverse
from rest_framework import status
from fcm_django.models import FCMDevice


class TestRegisterFCMDeviceView:
    """Тесты для RegisterFCMDeviceView"""

    def test_unauthenticated_access(self, api_client, fcm_device_data):
        """Неавторизованный пользователь получает 403"""

        url = reverse("register_fcm_device")
        response = api_client.post(url, fcm_device_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_register_new_device(self, api_client, student_user, fcm_device_data):
        """Регистрация нового устройства"""

        api_client.force_authenticate(user=student_user)
        url = reverse("register_fcm_device")

        response = api_client.post(url, fcm_device_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["created"] is True
        assert "device_id" in response.data

    def test_register_existing_device_updates_user(self, api_client, student_user, premium_user, fcm_device_data):
        """Существующий токен обновляется с новым пользователем"""

        # Создаём устройство для premium_user
        FCMDevice.objects.create(
            registration_id=fcm_device_data["token"],
            user=premium_user,
            type="web"
        )

        # Тот же токен регистрирует student_user
        api_client.force_authenticate(user=student_user)
        url = reverse("register_fcm_device")
        response = api_client.post(url, fcm_device_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["created"] is False

        # Проверяем, что устройство теперь принадлежит student_user
        device = FCMDevice.objects.get(registration_id=fcm_device_data["token"])
        assert device.user == student_user

    def test_register_without_token(self, api_client, student_user):
        """Запрос без токена возвращает 400"""

        api_client.force_authenticate(user=student_user)
        url = reverse("register_fcm_device")

        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_register_with_default_type(self, api_client, student_user):
        """Тип устройства по умолчанию — web"""

        api_client.force_authenticate(user=student_user)
        url = reverse("register_fcm_device")

        response = api_client.post(url, {"token": "test_token_no_type"})

        assert response.status_code == status.HTTP_200_OK

        device = FCMDevice.objects.get(registration_id="test_token_no_type")
        assert device.type == "web"
