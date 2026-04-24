from django.contrib import admin
from .models import Category, Word, UserWord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "word_count")
    list_display_links = ("name",)
    # Можно менять порядок тем прямо в списке
    list_editable = ("order",)
    search_fields = ("name", "description")
    # Автоматически создаёт slug из названия
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")

    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "description")
        }),
        ("Настройки отображения", {
            "fields": ("order",),
            "classes": ("collapse",)
        }),
    )

    def word_count(self, obj):
        """Количество слов в теме"""
        return obj.words.count()

    word_count.short_description = "Количество слов"


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("term", "category", "difficulty", "has_image", "has_audio", "is_active", "created_at")
    list_display_links = ("term",)
    list_filter = ("category", "difficulty", "is_active", "created_at")
    search_fields = ("term", "translation_description", "example_sentence")
    list_editable = ("difficulty", "is_active")

    fieldsets = (
        ("Основная информация", {
            "fields": ("category", "term", "transcription", "translation_description")
        }),
        ("Медиа", {
            "fields": ("image_url", "audio_url"),
            "classes": ("collapse",)
        }),
        ("Пример использования", {
            "fields": ("example_sentence",),
            "classes": ("collapse",)
        }),
        ("Настройки", {
            "fields": ("difficulty", "is_active"),
        }),
    )

    def has_image(self, obj):
        return bool(obj.image_url)

    has_image.boolean = True
    has_image.short_description = "Изображение"

    def has_audio(self, obj):
        return bool(obj.audio_url)

    has_audio.boolean = True
    has_audio.short_description = "Аудио"


@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = ("user", "word", "stage", "next_review_date", "is_deleted_by_user", "is_learned")
    list_filter = ("stage", "is_deleted_by_user", "is_learned", "user")
    search_fields = ("user__username", "word__term")
    list_editable = ("stage",)

    fieldsets = (
        ("Связи", {
            "fields": ("user", "word")
        }),
        ("SRS статистика", {
            "fields": ("stage", "next_review_date", "last_reviewed", "times_reviewed")
        }),
        ("Статусы", {
            "fields": ("is_deleted_by_user", "is_learned")
        }),
    )

    readonly_fields = ("last_reviewed", "times_reviewed", "date_added", "updated_at")
