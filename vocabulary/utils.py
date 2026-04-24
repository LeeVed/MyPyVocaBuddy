from django.utils import timezone
from .models import UserWord, Word


def add_base_words_to_user(user):
    """
    Добавляет все активные слова из глобальной БД в личный словарь пользователя.
    Вызывается после регистрации нового пользователя.
    """
    base_words = Word.objects.filter(is_active=True)
    created_count = 0

    for word in base_words:
        user_word, created = UserWord.objects.get_or_create(
            user=user,
            word=word,
            defaults={
                "stage": 0,
                "next_review_date": timezone.now(),
                "times_reviewed": 0,
                "is_deleted_by_user": False,
                "is_learned": False,
            }
        )
        if created:
            created_count += 1

    return created_count
