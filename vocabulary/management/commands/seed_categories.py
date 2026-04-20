from django.core.management.base import BaseCommand
from vocabulary.models import Category

class Command(BaseCommand):
    help = "Заполняет базу данных начальными темами"

    def handle(self, *args, **options):
        categories_data = [
            {"name": "Основы Python", "order": 1,
             "description": "Базовые понятия: переменные, типы данных, операторы, условные конструкции"},
            {"name": "Функции", "order": 2,
             "description": "Определение и использование функций, аргументы, return, lambda"},
            {"name": "Объектно-ориентированное программирование", "order": 3,
             "description": "Классы, объекты, наследование, полиморфизм, инкапсуляция"},
            {"name": "Работа с файлами", "order": 4,
             "description": "Чтение и запись файлов, контекстные менеджеры, with"},
            {"name": "Обработка ошибок", "order": 5,
             "description": "Исключения, try-except-else-finally, raise"},
            {"name": "Библиотеки и модули", "order": 6,
             "description": "Импорт модулей, pip, стандартная библиотека"},
            {"name": "Продвинутые темы", "order": 7,
             "description": "Декораторы, генераторы, итераторы, контекстные менеджеры"},
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "order": cat_data["order"],
                    "description": cat_data["description"]
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Создана тема: {category.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Тема уже существует: {category.name}"))

        self.stdout.write(self.style.SUCCESS(f"\nГотово! Создано новых тем: {created_count}"))
        