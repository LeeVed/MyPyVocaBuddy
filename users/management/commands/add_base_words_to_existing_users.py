from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from vocabulary.utils import add_base_words_to_user

User = get_user_model()


class Command(BaseCommand):
    help = "Добавляет базовые слова всем существующим пользователям, у которых нет слов"

    def handle(self, *args, **options):
        users = User.objects.filter(role="student")

        for user in users:
            if user.user_words.count() == 0:
                added = add_base_words_to_user(user)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Пользователю {user.username} добавлено {added} слов")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ У пользователя {user.username} уже есть слова")
                )
