from glin_profanity import Filter
from django.core.exceptions import ValidationError


pf = Filter({
    "languages": ["russian", "english"],  # Поддерживает русский и английский
    "case_sensitive": False,  # Не учитываем регистр
    "word_boundaries": True,  # Учитываем границы слов
    "replace_with": "***",  # Символы для цензуры
    "severity_levels": True,  # Уровни серьёзности (опционально)
})


def validate_no_profanity(value):
    """
    Проверяет текст на наличие нецензурных слов.
    Используется в формах для валидации пользовательского ввода.
    """
    if not isinstance(value, str):
        value = str(value)

    if pf.is_profane(value):
        raise ValidationError("Текст содержит неприемлемую лексику")


def validate_clean_text(value):
    """Проверяет текст и возвращает очищенную версию"""

    if not isinstance(value, str):
        value = str(value)

    if pf.is_profane(value):

        return pf.clean_text(value) if hasattr(pf, "clean_text") else value.replace("fuck", "****")
    return value


def is_text_clean(value):
    """
    Проверяет текст на наличие нецензурных слов.
    Возвращает True, если текст чистый, False — если содержит нецензурные слова.
    """
    if not isinstance(value, str):
        value = str(value)
    return not pf.is_profane(value)
