from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from firebase_admin import messaging
from vocabulary.models import UserWord

User = get_user_model()


@shared_task
def send_review_reminder():
    """Отправляет push-напоминания пользователям о необходимости повторить слова через FCM Topics."""

    # 1. Находим пользователей, у которых есть слова на повторение
    users_to_notify = User.objects.filter(role="student", is_active=True)

    sent_count = 0
    notified_user_ids = [] # для логирования, статистики и будущих личных сообщений

    for user in users_to_notify:
        words_count = UserWord.objects.filter(
            user=user,
            is_deleted_by_user=False,
            next_review_date__lte=timezone.now()
        ).count()

        if words_count > 0:
            notified_user_ids.append(user.id)
            sent_count += 1

    # 2. Если есть пользователи для оповещения, отправляем одно сообщение в топик
    if notified_user_ids:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🐍 Пора повторить слова!",
                body=f"У вас есть словa на повторении. Заходите в MyPyVocaBuddy!",
            ),
            topic="review_reminders",  # Отправляем в топик
            data={
                "type": "review_reminder",
            },
        )

        try:
            response = messaging.send(message)
            print(f"Push-уведомление отправлено в топик. ID сообщения: {response}")
        except Exception as e:
            print(f"Ошибка при отправке push-уведомления: {e}")
            return f"Ошибка: {e}"

    return f"Отправлено напоминаний (пользователей для оповещения): {sent_count}"
