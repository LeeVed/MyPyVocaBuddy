import pytest
from django.utils import timezone
from datetime import timedelta
from vocabulary.models import Category, Word, UserWord


class TestCategory:
    """Тесты для модели Category"""

    def test_create_category(self, db):
        """Создание категории"""

        category = Category.objects.create(
            name="Test Category",
            description="Test description"
        )
        assert category.name == "Test Category"
        assert category.slug == "test-category"
        assert str(category) == "Test Category"

    def test_slug_auto_generation(self, db):
        """Slug автоматически создаётся из name"""

        category = Category.objects.create(name="Python Basics")
        assert category.slug == "python-basics"

    def test_slug_cyrillic_support(self, db):
        """Slug корректно работает с кириллицей"""

        category = Category.objects.create(name="Основы Python")
        assert category.slug == "osnovy-python"

    def test_word_count_property(self, category, word):
        """Свойство word_count возвращает количество слов"""

        # Создаём второе слово в той же категории
        Word.objects.create(
            term="function",
            translation_description="Функция",
            category=category,
            difficulty=2
        )
        assert category.word_count == 2

    def test_ordering(self, category, second_category):
        """Проверка сортировки по order и name"""

        category.order = 2
        category.save()
        second_category.order = 1
        second_category.save()

        categories = Category.objects.all()
        assert categories[0] == second_category
        assert categories[1] == category


class TestWord:
    """Тесты для модели Word"""

    def test_create_word(self, word, category):
        """Создание слова"""

        assert word.term == "variable"
        assert word.category == category
        assert word.difficulty == 1
        assert word.is_active is True
        assert str(word) == "variable (Python Basics)"

    def test_has_image_property(self, word):
        """Свойство has_image"""

        assert word.has_image is False

        word.image_url = "https://example.com/image.jpg"
        word.save()
        assert word.has_image is True

    def test_has_audio_property(self, word):
        """Свойство has_audio"""

        assert word.has_audio is False

        word.audio_url = "https://example.com/audio.mp3"
        word.save()
        assert word.has_audio is True

    def test_ordering(self, word, second_word):
        """Слова сортируются по алфавиту"""

        words = Word.objects.all()
        assert words[0].term == "function"
        assert words[1].term == "variable"

    def test_difficulty_choices(self, db, category):
        """Проверка выбора сложности"""

        word = Word.objects.create(
            term="easy",
            translation_description="Easy",
            category=category,
            difficulty=1
        )
        assert word.get_difficulty_display() == "Легкий"

        word.difficulty = 3
        word.save()
        assert word.get_difficulty_display() == "Сложный"


class TestUserWord:
    """Тесты для модели UserWord"""

    def test_create_user_word(self, user_word, student_user, word):
        """Создание слова пользователя"""

        assert user_word.user == student_user
        assert user_word.word == word
        assert user_word.stage == 0
        assert user_word.times_reviewed == 0
        assert user_word.is_deleted_by_user is False

    def test_display_term_global(self, user_word):
        """display_term для глобального слова"""

        assert user_word.display_term == "variable"

    def test_display_term_custom(self, custom_user_word):
        """display_term для пользовательского слова"""

        assert custom_user_word.display_term == "list_comprehension"

    def test_display_description_global(self, user_word):
        """display_description для глобального слова"""

        assert user_word.display_description == "Переменная — именованная область памяти"

    def test_display_description_custom(self, custom_user_word):
        """display_description для пользовательского слова"""

        assert custom_user_word.display_description == "Генератор списков в Python"

    def test_display_transcription_global(self, user_word):
        """display_transcription для глобального слова"""

        assert user_word.display_transcription == "ˈverēəbəl"

    def test_display_transcription_custom(self, custom_user_word):
        """display_transcription для пользовательского слова"""

        assert custom_user_word.display_transcription == "lɪst ˌkɑmprɪˈhɛnʃən"

    def test_update_stage_correct(self, user_word):
        """Правильный ответ повышает stage"""

        assert user_word.stage == 0
        user_word.update_stage(is_correct=True)

        assert user_word.stage == 1
        assert user_word.times_reviewed == 1
        assert user_word.last_reviewed is not None

    def test_update_stage_incorrect(self, user_word):
        """Неправильный ответ сбрасывает stage"""

        user_word.stage = 3
        user_word.save()

        user_word.update_stage(is_correct=False)

        assert user_word.stage == 0
        assert user_word.times_reviewed == 1

    def test_update_stage_max_stage(self, user_word):
        """Stage не превышает 5"""

        user_word.stage = 5
        user_word.save()

        user_word.update_stage(is_correct=True)
        assert user_word.stage == 5

    def test_update_stage_sets_learned(self, user_word):
        """При достижении stage 5 слово помечается как выученное"""

        user_word.stage = 4
        user_word.save()

        user_word.update_stage(is_correct=True)

        assert user_word.stage == 5
        assert user_word.is_learned is True

    def test_update_stage_next_review_date(self, user_word):
        """Проверка расчёта даты следующего повторения"""

        user_word.update_stage(is_correct=True)  # stage 1 -> 1 день

        expected_date = timezone.now() + timedelta(days=1)
        actual_date = user_word.next_review_date

        assert abs((actual_date - expected_date).total_seconds()) < 1

    def test_hide_for_premium_premium_user(self, premium_user, word):
        """Premium пользователь может скрыть слово"""

        user_word = UserWord.objects.create(
            user=premium_user,
            word=word,
            stage=0
        )
        result = user_word.hide_for_premium()

        assert result is True
        user_word.refresh_from_db()
        assert user_word.is_deleted_by_user is True

    def test_hide_for_premium_free_user(self, student_user, word):
        """Free пользователь не может скрыть слово"""

        user_word = UserWord.objects.create(
            user=student_user,
            word=word,
            stage=0
        )
        result = user_word.hide_for_premium()

        assert result is False
        user_word.refresh_from_db()
        assert user_word.is_deleted_by_user is False

    def test_restore_for_premium(self, hidden_user_word):
        """Premium пользователь может восстановить скрытое слово"""

        result = hidden_user_word.restore_for_premium()

        assert result is True
        hidden_user_word.refresh_from_db()
        assert hidden_user_word.is_deleted_by_user is False

    def test_needs_review_property(self, user_word):
        """Свойство needs_review"""

        # Дата в прошлом — нужно повторить
        assert user_word.needs_review is True

        # Дата в будущем — не нужно
        user_word.next_review_date = timezone.now() + timedelta(days=7)
        user_word.save()
        assert user_word.needs_review is False

    def test_needs_review_hidden_word(self, hidden_user_word):
        """Скрытое слово не требует повторения"""

        hidden_user_word.next_review_date = timezone.now() - timedelta(days=1)
        hidden_user_word.save()
        assert hidden_user_word.needs_review is False

    def test_is_new_property(self, user_word):
        """Свойство is_new"""

        assert user_word.is_new is True

        user_word.times_reviewed = 1
        user_word.save()
        assert user_word.is_new is False

    def test_days_until_review(self, user_word):
        """Свойство days_until_review"""
        # Требует повторения сейчас
        assert user_word.days_until_review == 0

        # Повторение через 7 дней
        user_word.next_review_date = timezone.now() + timedelta(days=7)
        user_word.save()
        # Допускаем погрешность в 1 день из-за округления
        assert user_word.days_until_review in [6, 7]

    def test_get_review_session(self, student_user, review_session_words):
        """Метод get_review_session возвращает слова для повторения"""

        session = UserWord.get_review_session(student_user, limit=3)

        assert len(session) == 3
        assert all(isinstance(uw, UserWord) for uw in session)

    def test_get_review_session_respects_limit(self, student_user, review_session_words):
        """Метод get_review_session соблюдает лимит"""

        session = UserWord.get_review_session(student_user, limit=2)
        assert len(session) == 2

    def test_get_review_session_excludes_hidden(self, hidden_user_word):
        """Метод get_review_session исключает скрытые слова"""

        hidden_user_word.next_review_date = timezone.now() - timedelta(days=1)
        hidden_user_word.save()

        session = UserWord.get_review_session(hidden_user_word.user, limit=10)
        assert hidden_user_word not in session

    def test_unique_constraint(self, student_user, word):
        """Нельзя создать два UserWord для одного пользователя и одного Word"""

        UserWord.objects.create(user=student_user, word=word, stage=0)

        with pytest.raises(Exception):
            UserWord.objects.create(user=student_user, word=word, stage=0)

    def test_str_representation(self, user_word):
        """Строковое представление UserWord"""

        assert str(user_word) == "teststudent — variable (этап 0)"

    def test_str_representation_hidden(self, hidden_user_word):
        """Строковое представление скрытого слова"""

        assert str(hidden_user_word) == "premiumuser — variable (скрыто)"

    def test_str_representation_custom(self, custom_user_word):
        """Строковое представление пользовательского слова"""

        assert str(custom_user_word) == "premiumuser — list_comprehension (этап 0)"
