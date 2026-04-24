from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fcm_django.models import FCMDevice


class RegisterFCMDeviceView(APIView):
    """
    Регистрирует или обновляет FCM-токен устройства.
    Если токен уже существует (тот же браузер) — привязываем к новому пользователю.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        device_type = request.data.get("type", "web")

        if not token:
            return Response({"error": "Token is required"}, status=400)

        # Ищем устройство с таким токеном
        device = FCMDevice.objects.filter(registration_id=token).first()

        if device:
            # Токен уже существует — обновляем владельца
            device.user = request.user
            device.type = device_type
            device.active = True
            device.save()
            created = False
        else:
            # Новый токен — создаём запись
            device = FCMDevice.objects.create(
                registration_id=token,
                user=request.user,
                type=device_type,
                active=True
            )
            created = True

        return Response({
            "success": True,
            "message": "Device registered successfully",
            "device_id": device.id,
            "created": created
        })
