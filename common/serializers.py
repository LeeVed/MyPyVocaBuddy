from rest_framework import serializers
from vocabulary.models import UserWord


class UserWordSerializer(serializers.ModelSerializer):
    """Сериализатор для слова пользователя (флеш-карты)"""

    term = serializers.SerializerMethodField()
    transcription = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    audio = serializers.SerializerMethodField()
    needs_review = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserWord
        fields = ["id", "term", "transcription", "description", "image", "audio", "stage", "needs_review"]

    def get_term(self, obj):
        return obj.display_term

    def get_transcription(self, obj):
        return obj.display_transcription

    def get_description(self, obj):
        return obj.display_description

    def get_image(self, obj):
        return obj.display_image

    def get_audio(self, obj):
        if obj.word and obj.word.audio_url:
            return obj.word.audio_url
        return None


class PronunciationCheckSerializer(serializers.Serializer):
    """Сериализатор для проверки произношения"""

    user_word_id = serializers.IntegerField()
    spoken_text = serializers.CharField(max_length=500)


class WrittenAnswerSerializer(serializers.Serializer):
    """Сериализатор для письменного ответа"""

    user_word_id = serializers.IntegerField()
    answer = serializers.CharField(max_length=500)


class NextWordSerializer(serializers.Serializer):
    """Сериализатор для перехода к следующему слову"""

    user_word_id = serializers.IntegerField(required=False, allow_null=True)
    user_choice = serializers.ChoiceField(
        choices=["know", "doubt", "dont_know"],
        required=False,
        allow_null=True
    )


class HideWordSerializer(serializers.Serializer):
    """Сериализатор для скрытия/восстановления слова"""

    user_word_id = serializers.IntegerField()
