from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "speaker", "level", "duration_minutes", "is_premium", "is_active")
    list_filter = ("level", "is_premium", "is_active")
    search_fields = ("title", "speaker", "topic", "description")
    list_editable = ("is_premium", "is_active")

    fieldsets = (
        ("Основная информация", {
            "fields": ("title", "speaker", "topic", "youtube_url", "description", "level")
        }),
        ("Доступ", {
            "fields": ("is_premium", "is_active")
        }),
        ("Слова из видео", {
            "fields": ("words",),
            "classes": ("collapse",)
        }),
        ("Дополнительно", {
            "fields": ("duration",),
            "classes": ("collapse",)
        }),
    )

    def duration_minutes(self, obj):
        if obj.duration:
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            return f"{minutes}:{seconds:02d}"
        return "—"

    duration_minutes.short_description = "Длительность"
