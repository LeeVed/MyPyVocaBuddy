from vocabulary.utils import add_base_words_to_user
from vocabulary.models import UserWord, Word
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAddBaseWordsToUser:
    """Тесты для add_base_words_to_user"""

    def test_adds_only_active_words(self, db, category, word, second_word, inactive_word):
        """Добавляются только активные слова"""

        user = User.objects.create_user(
            username="newuser",
            password="testpass123"
        )
        
        # word и second_word активны, inactive_word — нет
        added_count = add_base_words_to_user(user)
        
        assert added_count == 2
        assert UserWord.objects.filter(user=user).count() == 2
        
        # Проверяем, что неактивное слово не добавлено
        terms = [uw.display_term for uw in UserWord.objects.filter(user=user)]
        assert "variable" in terms
        assert "function" in terms
        assert "deprecated" not in terms

    def test_does_not_duplicate_existing_words(self, db, student_user, word):
        """Существующие слова не дублируются"""

        Word.objects.all().update(is_active=False)
        # Активируем только нужное слово
        word.is_active = True
        word.save()
        # Создаём UserWord для студента
        from vocabulary.models import UserWord
        UserWord.objects.create(
            user=student_user,
            word=word,
            stage=0
        )

        initial_count = UserWord.objects.filter(user=student_user).count()
        added_count = add_base_words_to_user(student_user)

        assert added_count == 0
        assert UserWord.objects.filter(user=student_user).count() == initial_count

    def test_returns_created_count(self, db, category):
        """Функция возвращает количество созданных слов"""

        user = User.objects.create_user(username="newuser", password="test")

        for i in range(3):
            Word.objects.create(
                term=f"word_{i}",
                translation_description=f"Desc {i}",
                category=category,
                difficulty=1
            )
        
        added_count = add_base_words_to_user(user)
        assert added_count == 3

    def test_creates_user_words_with_correct_defaults(self, db, category):
        """Созданные UserWord имеют правильные значения по умолчанию"""

        user = User.objects.create_user(username="newuser", password="test")
        word = Word.objects.create(
            term="test",
            translation_description="Test",
            category=category,
            difficulty=1
        )
        
        add_base_words_to_user(user)
        
        user_word = UserWord.objects.get(user=user, word=word)
        assert user_word.stage == 0
        assert user_word.times_reviewed == 0
        assert user_word.is_deleted_by_user is False
        assert user_word.is_learned is False
