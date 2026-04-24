from unittest.mock import patch
from django.utils import timezone
from users.tasks import send_review_reminder
from vocabulary.models import UserWord, Word
from django.contrib.auth import get_user_model

User = get_user_model()


class TestSendReviewReminder:
    """Тесты для send_review_reminder"""

    @patch("users.tasks.messaging.send")
    def test_send_reminder_to_users_with_words(self, mock_send, db, student_user, category):
        """Отправка напоминания пользователям со словами на повторение"""
        # Создаём слово для повторения
        word = Word.objects.create(
            term="test_word",
            translation_description="Test description",
            category=category,
            difficulty=1
        )
        UserWord.objects.create(
            user=student_user,
            word=word,
            stage=0,
            next_review_date=timezone.now() - timezone.timedelta(days=1)
        )

        mock_send.return_value = "message_id_123"

        result = send_review_reminder()

        assert "Отправлено напоминаний" in result
        assert "1" in result
        mock_send.assert_called_once()

    @patch("users.tasks.messaging.send")
    def test_no_reminder_when_no_words(self, mock_send, db, student_user):
        """Напоминание не отправляется, если нет слов на повторение"""
        result = send_review_reminder()

        assert "Отправлено напоминаний (пользователей для оповещения): 0" in result
        mock_send.assert_not_called()

    @patch("users.tasks.messaging.send")
    def test_only_active_students_receive_reminders(self, mock_send, db):
        """Только активные студенты получают напоминания"""
        # Создаём неактивного пользователя
        inactive_user = User.objects.create_user(
            username="inactive",
            password="test",
            role="student",
            is_active=False
        )

        result = send_review_reminder()

        assert "0" in result  # никто не получил
        mock_send.assert_not_called()

    @patch("users.tasks.messaging.send")
    def test_moderators_not_receive_reminders(self, mock_send, db, moderator_user, category):
        """Модераторы не получают напоминания"""
        word = Word.objects.create(
            term="test_word",
            translation_description="Test",
            category=category,
            difficulty=1
        )
        UserWord.objects.create(
            user=moderator_user,
            word=word,
            stage=0,
            next_review_date=timezone.now() - timezone.timedelta(days=1)
        )

        result = send_review_reminder()

        assert "0" in result
        mock_send.assert_not_called()

    @patch("users.tasks.messaging.send")
    def test_handles_firebase_error(self, mock_send, db, student_user, category):
        """Обработка ошибки Firebase"""
        word = Word.objects.create(
            term="test_word",
            translation_description="Test",
            category=category,
            difficulty=1
        )
        UserWord.objects.create(
            user=student_user,
            word=word,
            stage=0,
            next_review_date=timezone.now() - timezone.timedelta(days=1)
        )

        mock_send.side_effect = Exception("Firebase error")

        result = send_review_reminder()

        assert "Ошибка" in result
