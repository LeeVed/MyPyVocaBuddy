from django.core.management.base import BaseCommand
from vocabulary.models import Category, Word


class Command(BaseCommand):
    help = "Заполняет базу данных начальными словами"

    def handle(self, *args, **options):
        # Получаем категории
        try:
            basics = Category.objects.get(name="Основы Python")
            functions = Category.objects.get(name="Функции")
            oop = Category.objects.get(name="Объектно-ориентированное программирование")
            errors = Category.objects.get(name="Обработка ошибок")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Сначала выполните команду seed_categories"))
            return

        words_data = [
            # Основы Python
            {"category": basics, "term": "variable",
             "transcription": "/ˈver.i.ə.bəl/",
             "translation_description": "Переменная — именованная область памяти для хранения данных",
             "difficulty": 1,
             "example_sentence": "x = 10 creates a variable x with value 10"},

            {"category": basics, "term": "string",
             "transcription": "/strɪŋ/",
             "translation_description": "Строка — последовательность символов",
             "difficulty": 1,
             "example_sentence": "name = 'Python' is a string variable"},

            {"category": basics, "term": "integer",
             "transcription": "/ˈɪn.tɪ.dʒər/",
             "translation_description": "Целое число — числовой тип данных без дробной части",
             "difficulty": 1,
             "example_sentence": "age = 25 stores an integer value"},

            {"category": basics, "term": "list",
             "transcription": "/lɪst/",
             "translation_description": "Список — упорядоченная изменяемая коллекция элементов",
             "difficulty": 1,
             "example_sentence": "fruits = ['apple', 'banana', 'cherry'] is a list"},

            {"category": basics, "term": "dictionary",
             "transcription": "/ˈdɪk.ʃən.ər.i/",
             "translation_description": "Словарь — коллекция пар 'ключ-значение'",
             "difficulty": 2,
             "example_sentence": "person = {'name': 'John', 'age': 30} is a dictionary"},

            # Функции
            {"category": functions, "term": "function",
             "transcription": "/ˈfʌŋk.ʃən/",
             "translation_description": "Функция — блок кода, который выполняет определенную задачу",
             "difficulty": 1,
             "example_sentence": "The print() function outputs text to the console"},

            {"category": functions, "term": "argument",
             "transcription": "/ˈɑːɡ.jə.mənt/",
             "translation_description": "Аргумент — значение, передаваемое в функцию",
             "difficulty": 2,
             "example_sentence": "The function takes two arguments: name and age"},

            {"category": functions, "term": "return",
             "transcription": "/rɪˈtɜːn/",
             "translation_description": "Возврат — выход из функции с передачей значения",
             "difficulty": 2,
             "example_sentence": "The return statement sends a value back to the caller"},

            {"category": functions, "term": "lambda",
             "transcription": "/ˈlæm.də/",
             "translation_description": "Лямбда-функция — анонимная функция",
             "difficulty": 3,
             "example_sentence": "square = lambda x: x**2 creates an anonymous function"},

            # ООП
            {"category": oop, "term": "class",
             "transcription": "/klɑːs/",
             "translation_description": "Класс — шаблон для создания объектов",
             "difficulty": 2,
             "example_sentence": "class Dog: defines a new class"},

            {"category": oop, "term": "object",
             "transcription": "/ˈɒb.dʒɪkt/",
             "translation_description": "Объект — экземпляр класса",
             "difficulty": 2,
             "example_sentence": "my_dog = Dog() creates an object"},

            {"category": oop, "term": "inheritance",
             "transcription": "/ɪnˈher.ɪ.təns/",
             "translation_description": "Наследование — механизм создания классов на основе существующих",
             "difficulty": 3,
             "example_sentence": "class Cat(Animal): inherits from Animal class"},

            # Обработка ошибок
            {"category": errors, "term": "exception",
             "transcription": "/ɪkˈsep.ʃən/",
             "translation_description": "Исключение — ошибка, возникающая во время выполнения",
             "difficulty": 2,
             "example_sentence": "Try-except blocks handle exceptions gracefully"},

            {"category": errors, "term": "try",
             "transcription": "/traɪ/",
             "translation_description": "Попытаться — блок для проверки кода на ошибки",
             "difficulty": 2,
             "example_sentence": "The try block contains code that might raise an exception"},
        ]

        created_count = 0
        for word_data in words_data:
            word, created = Word.objects.get_or_create(
                term=word_data["term"],
                defaults={
                    "category": word_data["category"],
                    "transcription": word_data.get("transcription", ""),
                    "translation_description": word_data["translation_description"],
                    "difficulty": word_data.get("difficulty", 1),
                    "example_sentence": word_data.get("example_sentence", ""),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Добавлено слово: {word.term}"))

        self.stdout.write(self.style.SUCCESS(f"\nГотово! Добавлено новых слов: {created_count}"))
        