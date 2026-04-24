from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Заполняет проект начальными данными (пользователи, темы, слова)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Начинаем заполнение проекта...\n"))

        # 1. Пользователи
        self.stdout.write("Шаг 1: Создание пользователей...")
        call_command("seed_users")

        # 2. Темы
        self.stdout.write("\nШаг 2: Создание тем...")
        call_command("seed_categories")

        # 3. Слова
        self.stdout.write("\nШаг 3: Создание слов...")
        call_command("seed_words")

        # 4. Слова пользователям
        self.stdout.write("\nШаг 4: Добавление слов пользователям...")
        call_command("seed_user_words")

        self.stdout.write(self.style.SUCCESS("\nПроект полностью заполнен начальными данными!"))
        