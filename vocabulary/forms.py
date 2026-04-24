from django import forms
from django.utils import timezone
from .models import UserWord
from common.validators import validate_no_profanity


class CustomWordForm(forms.Form):
    """Форма для добавления своих слов только для Premium"""

    term = forms.CharField(
        max_length=200,
        label="Термин (англ.)",
        validators=[validate_no_profanity],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "например, asynchronous"
        })
    )

    transcription = forms.CharField(
        max_length=100,
        required=False,
        label="Транскрипция",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "например, /ˌeɪ.sɪŋˈkrɒ.nəs/"
        })
    )

    description = forms.CharField(
        label="Описание / перевод",
        validators=[validate_no_profanity],
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Значение слова на русском или определение..."
        })
    )

    image = forms.ImageField(
        required=False,
        label="Изображение",
        help_text="Необязательно. Можно загрузить картинку для ассоциации"
    )

    def save(self, user):
        """Сохраняет слово в личный словарь пользователя"""

        user_word = UserWord(
            user=user,
            word=None,
            custom_term=self.cleaned_data["term"],
            custom_transcription=self.cleaned_data.get("transcription", ""),
            custom_description=self.cleaned_data["description"],
            custom_image=self.cleaned_data.get("image"),
            stage=0,  # новое слово
            next_review_date=timezone.now(),
            times_reviewed=0,
            is_deleted_by_user=False,
            is_learned=False,
        )
        user_word.save()
        return user_word
