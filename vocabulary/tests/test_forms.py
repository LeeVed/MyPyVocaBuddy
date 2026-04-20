from vocabulary.forms import CustomWordForm


class TestCustomWordForm:
    """Тесты для CustomWordForm"""

    def test_form_valid_data(self, valid_custom_word_data):
        """Форма валидна с правильными данными"""

        form = CustomWordForm(data=valid_custom_word_data)
        assert form.is_valid()

    def test_form_invalid_missing_term(self, invalid_custom_word_data):
        """Форма невалидна без term"""

        form = CustomWordForm(data=invalid_custom_word_data)
        assert not form.is_valid()
        assert "term" in form.errors

    def test_form_transcription_optional(self):
        """Поле transcription необязательно"""

        data = {
            "term": "test",
            "description": "Test description"
        }
        form = CustomWordForm(data=data)
        assert form.is_valid()

    def test_form_save_creates_user_word(self, premium_user, valid_custom_word_data):
        """Форма создаёт UserWord для Premium пользователя"""

        form = CustomWordForm(data=valid_custom_word_data)
        assert form.is_valid()

        user_word = form.save(premium_user)

        assert user_word.user == premium_user
        assert user_word.custom_term == "decorator"
        assert user_word.custom_transcription == "ˈdekəˌrādər"
        assert user_word.custom_description == "Декоратор — функция, модифицирующая поведение другой функции"
        assert user_word.word is None
        assert user_word.stage == 0
        assert user_word.times_reviewed == 0
        assert user_word.is_deleted_by_user is False

    def test_form_save_without_transcription(self, premium_user):
        """Форма сохраняет слово без транскрипции"""

        data = {
            "term": "hello",
            "description": "A greeting word"
        }
        form = CustomWordForm(data=data)

        # Отладка: если форма невалидна, вывести ошибки
        if not form.is_valid():
            print(f"\nForm errors: {form.errors}")

        assert form.is_valid()

        user_word = form.save(premium_user)
        assert user_word.custom_transcription == ""

    def test_form_profanity_validation(self):
        """Форма невалидна при нецензурной лексике"""

        data = {
            "term": "fuck",
            "description": "Description"
        }
        form = CustomWordForm(data=data)
        assert not form.is_valid()
        assert "term" in form.errors
