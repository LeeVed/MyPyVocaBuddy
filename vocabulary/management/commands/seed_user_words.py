from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from vocabulary.models import Word, UserWord

User = get_user_model()


class Command(BaseCommand):
    help = "Добавляет слова пользователям для тестирования SRS системы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Добавить слова только указанному пользователю (по умолчанию всем)",
        )
        parser.add_argument(
            "--words-count",
            type=int,
            default=10,
            help="Количество слов для добавления (по умолчанию 10)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        words_count = options["words_count"]

        # Получаем пользователей
        if username:
            users = User.objects.filter(username=username)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"Пользователь '{username}' не найден"))
                return
        else:
            # Только студенты  — исключаем модераторов и админа
            users = User.objects.filter(role="student", is_superuser=False)
            if not users.exists():
                self.stdout.write(self.style.WARNING("Нет студентов для добавления слов"))
                return
        # Получаем активные слова
        words = Word.objects.filter(is_active=True)[:words_count]
        if not words.exists():
            self.stdout.write(self.style.ERROR("Нет активных слов в базе. Сначала выполните seed_words"))
            return

        total_added = 0

        for user in users:
            # Дополнительная проверка: только студенты
            if user.role != "student":
                continue

            added_count = 0
            for word in words:
                # Проверяем, есть ли уже это слово у пользователя
                user_word, created = UserWord.objects.get_or_create(
                    user=user,
                    word=word,
                    defaults={
                        "stage": 0,
                        "next_review_date": timezone.now(),
                        "times_reviewed": 0,
                        "is_deleted_by_user": False,
                        "is_learned": False,
                    },
                )
                if created:
                    added_count += 1
                    total_added += 1

            self.stdout.write(
                self.style.SUCCESS(f"Пользователю '{user.username}' добавлено слов: {added_count}")
            )

        self.stdout.write(self.style.SUCCESS(f"\nГотово! Всего добавлено слов: {total_added}"))
