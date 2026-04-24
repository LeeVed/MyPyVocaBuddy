from common.serializers import (
    UserWordSerializer,
    PronunciationCheckSerializer,
    WrittenAnswerSerializer,
    NextWordSerializer,
    HideWordSerializer
)
from vocabulary.models import UserWord


class TestUserWordSerializer:
    """Тесты для UserWordSerializer"""

    def test_serializer_includes_all_fields(self, user_word):
        """Сериализатор включает все необходимые поля"""

        serializer = UserWordSerializer(user_word)
        data = serializer.data

        expected_fields = ["id", "term", "transcription", "description",
                          "image", "audio", "stage", "needs_review"]
        for field in expected_fields:
            assert field in data

    def test_term_from_display_term(self, user_word):
        """Поле term получается из display_term"""

        serializer = UserWordSerializer(user_word)
        assert serializer.data["term"] == user_word.display_term

    def test_transcription_from_display_transcription(self, user_word):
        """Поле transcription получается из display_transcription"""

        serializer = UserWordSerializer(user_word)
        assert serializer.data["transcription"] == user_word.display_transcription

    def test_description_from_display_description(self, user_word):
        """Поле description получается из display_description"""

        serializer = UserWordSerializer(user_word)
        assert serializer.data["description"] == user_word.display_description

    def test_image_from_display_image(self, user_word):
        """Поле image получается из display_image"""

        serializer = UserWordSerializer(user_word)
        assert serializer.data["image"] == user_word.display_image

    def test_audio_handles_none(self, user_word):
        """Поле audio корректно обрабатывает None"""

        serializer = UserWordSerializer(user_word)
        assert serializer.data["audio"] is None

    def test_needs_review_field(self, user_word):
        """Поле needs_review корректно вычисляется"""

        serializer = UserWordSerializer(user_word)
        assert "needs_review" in serializer.data
        assert isinstance(serializer.data["needs_review"], bool)

    def test_custom_word_serialization(self, student_user):
        """Сериализация пользовательского слова без связи с Word"""

        custom_word = UserWord.objects.create(
            user=student_user,
            custom_term="my_custom_function",
            custom_description="My custom description",
            stage=1
        )
        serializer = UserWordSerializer(custom_word)
        data = serializer.data

        assert data["term"] == "my_custom_function"
        assert data["description"] == "My custom description"
        assert data["transcription"] == ""
        assert data["audio"] is None


class TestPronunciationCheckSerializer:
    """Тесты для PronunciationCheckSerializer"""

    def test_valid_data(self):
        """Сериализатор принимает валидные данные"""

        data = {"user_word_id": 1, "spoken_text": "variable"}
        serializer = PronunciationCheckSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["user_word_id"] == 1
        assert serializer.validated_data["spoken_text"] == "variable"

    def test_missing_fields(self):
        """Пропущенные поля вызывают ошибку валидации"""

        data = {"user_word_id": 1}
        serializer = PronunciationCheckSerializer(data=data)
        assert not serializer.is_valid()
        assert "spoken_text" in serializer.errors

    def test_empty_spoken_text(self):
        """Пустой spoken_text невалиден"""

        data = {"user_word_id": 1, "spoken_text": ""}
        serializer = PronunciationCheckSerializer(data=data)
        assert not serializer.is_valid()

    def test_long_spoken_text(self):
        """Слишком длинный spoken_text невалиден"""

        data = {"user_word_id": 1, "spoken_text": "a" * 501}
        serializer = PronunciationCheckSerializer(data=data)
        assert not serializer.is_valid()


class TestWrittenAnswerSerializer:
    """Тесты для WrittenAnswerSerializer"""

    def test_valid_data(self):
        """Сериализатор принимает валидные данные"""

        data = {"user_word_id": 1, "answer": "function"}
        serializer = WrittenAnswerSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_fields(self):
        """Пропущенные поля вызывают ошибку валидации"""

        data = {"user_word_id": 1}
        serializer = WrittenAnswerSerializer(data=data)
        assert not serializer.is_valid()
        assert "answer" in serializer.errors

    def test_long_answer(self):
        """Слишком длинный ответ невалиден"""

        data = {"user_word_id": 1, "answer": "a" * 501}
        serializer = WrittenAnswerSerializer(data=data)
        assert not serializer.is_valid()


class TestNextWordSerializer:
    """Тесты для NextWordSerializer"""

    def test_valid_choices(self):
        """Сериализатор принимает валидные choices"""

        valid_choices = ["know", "doubt", "dont_know"]
        for choice in valid_choices:
            data = {"user_word_id": 1, "user_choice": choice}
            serializer = NextWordSerializer(data=data)
            assert serializer.is_valid()

    def test_invalid_choice(self):
        """Невалидный choice отклоняется"""

        data = {"user_word_id": 1, "user_choice": "invalid"}
        serializer = NextWordSerializer(data=data)
        assert not serializer.is_valid()

    def test_optional_fields(self):
        """Поля необязательны"""
        data = {}
        serializer = NextWordSerializer(data=data)
        assert serializer.is_valid()


class TestHideWordSerializer:
    """Тесты для HideWordSerializer"""

    def test_valid_data(self):
        """Сериализатор принимает валидные данные"""

        data = {"user_word_id": 1}
        serializer = HideWordSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_user_word_id(self):
        """Пропущенный user_word_id вызывает ошибку"""

        data = {}
        serializer = HideWordSerializer(data=data)
        assert not serializer.is_valid()
