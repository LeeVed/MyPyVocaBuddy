from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей (admin, moderator, student_free, student_premium)"

    def handle(self, *args, **options):
        users_data = [
            {
                "username": "moderator",
                "email": "moderator@example.com",
                "password": "moder123",
                "role": "moderator",
                "subscription_type": "free",
                "city": "Saint Petersburg",
                "country": "Russia",
                "bio": "Модератор контента",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "student_free",
                "email": "free@example.com",
                "password": "student123",
                "role": "student",
                "subscription_type": "free",
                "city": "Novosibirsk",
                "country": "Russia",
                "bio": "Начинаю изучать Python!",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "student_premium",
                "email": "premium@example.com",
                "password": "premium123",
                "role": "student",
                "subscription_type": "premium",
                "language_level": "beginner",
                "preferred_language": "en",
                "city": "London",
                "country": "UK",
                "bio": "Premium user learning Python",
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        created_count = 0
        for user_data in users_data:
            username = user_data["username"]

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"Пользователь уже существует: {username}"))
                continue

            User.objects.create_user(
                username=username,
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"],
                subscription_type=user_data.get("subscription_type", "free"),
                language_level=user_data.get("language_level", None),
                preferred_language=user_data.get("preferred_language", "ru"),
                city=user_data.get("city", ""),
                country=user_data.get("country", ""),
                bio=user_data.get("bio", ""),
                is_staff=user_data.get("is_staff", False),
                is_superuser=user_data.get("is_superuser", False),
            )

            created_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"Создан пользователь: {username} (роль: {user_data['role']})"
            ))

        self.stdout.write(self.style.SUCCESS(f"\nГотово! Создано новых пользователей: {created_count}"))
