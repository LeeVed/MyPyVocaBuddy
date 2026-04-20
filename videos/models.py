from django.db import models
from django.urls import reverse
from vocabulary.models import Word


class Video(models.Model):
    """Модель видео для видеотеки"""

    LEVEL_CHOICES = [
        ("beginner", "Начинающий"),
        ("intermediate", "Средний"),
        ("advanced", "Продвинутый"),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Название видео"
    )
    youtube_url = models.URLField(
        verbose_name="Ссылка на YouTube"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание видео"
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="beginner",
        verbose_name="Уровень сложности"
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name="Только для Premium"
    )
    words = models.ManyToManyField(
        Word,
        blank=True,
        related_name="videos",
        verbose_name="Слова из видео"
    )
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Длительность в секундах (опционально)",
        verbose_name="Длительность"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )
    speaker = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Спикер"
    )
    topic = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Тема"
    )

    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("videos:detail", args=[self.pk])

    @property
    def youtube_embed_url(self):
        """Возвращает URL для встраивания видео"""
        # Короткая ссылка youtu.be
        if "youtu.be" in self.youtube_url:
            video_id = self.youtube_url.split("/")[-1]    # берём последний элемент
        # Обычная ссылка с v=
        elif "v=" in self.youtube_url:
            video_id = self.youtube_url.split("v=")[1].split("&")[0]
        # Неизвестный формат
        else:
            return self.youtube_url
        return f"https://www.youtube.com/embed/{video_id}"

    @property
    def duration_minutes(self):
        """Возвращает длительность в минутах (если указана)"""

        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes} мин {seconds} сек"
        return "—"
