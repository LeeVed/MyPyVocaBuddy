import pytest
from django.core.exceptions import ValidationError
from common.validators import (
    validate_no_profanity,
    validate_clean_text,
    is_text_clean
)


class TestValidateNoProfanity:
    """Тесты для validate_no_profanity"""

    def test_clean_text_passes(self):
        """Чистый текст проходит валидацию"""

        clean_texts = [
            "Hello world",
            "Python programming",
            "Learning Django",
            "Привет мир",
            "Изучаем Python",
        ]
        for text in clean_texts:
            try:
                validate_no_profanity(text)
            except ValidationError:
                pytest.fail(f"Clean text '{text}' raised ValidationError")

    def test_profane_text_raises_error(self):
        """Текст с нецензурными словами вызывает ошибку"""

        profane_texts = ["fuck this", "shit happens"]
        for text in profane_texts:
            with pytest.raises(ValidationError) as exc_info:
                validate_no_profanity(text)
            assert "неприемлемую лексику" in str(exc_info.value)

    def test_mixed_case_profanity(self):
        """Проверка не чувствительна к регистру"""

        with pytest.raises(ValidationError):
            validate_no_profanity("FuCk")

    def test_non_string_input_converted(self):
        """Не-строковые значения конвертируются в строку"""

        try:
            validate_no_profanity(12345)
        except ValidationError:
            pytest.fail("Non-string input should be converted")

        try:
            validate_no_profanity(None)
        except ValidationError:
            pytest.fail("None should be converted to string")


class TestValidateCleanText:
    """Тесты для validate_clean_text"""

    def test_clean_text_unchanged(self):
        """Чистый текст возвращается без изменений"""

        text = "Hello world"
        result = validate_clean_text(text)
        assert result == text

    def test_profane_text_censored(self):
        """Нецензурный текст цензурируется"""

        text = "fuck this shit"
        result = validate_clean_text(text)
        assert result != text
        assert "***" in result
        assert len(result) > 0

    def test_non_string_input_converted(self):
        """Не-строковые значения конвертируются"""

        result = validate_clean_text(12345)
        assert isinstance(result, str)
        assert result == "12345"


class TestIsTextClean:
    """Тесты для is_text_clean"""

    def test_clean_text_returns_true(self):
        """Чистый текст возвращает True"""

        assert is_text_clean("Hello world") is True
        assert is_text_clean("Python programming") is True
        assert is_text_clean("Привет мир") is True

    def test_profane_text_returns_false(self):
        """Нецензурный текст возвращает False"""

        assert is_text_clean("fuck") is False

    def test_non_string_input(self):
        """Не-строковые значения обрабатываются корректно"""

        assert is_text_clean(12345) is True
        assert is_text_clean(None) is True
        assert is_text_clean(True) is True

    def test_empty_string(self):
        """Пустая строка считается чистой"""

        assert is_text_clean("") is True

    def test_whitespace_string(self):
        """Строка из пробелов считается чистой"""

        assert is_text_clean("   ") is True
