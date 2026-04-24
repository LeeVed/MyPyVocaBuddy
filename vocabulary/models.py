from django.db import models
from django.urls import reverse
from slugify import slugify
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class Category(models.Model):
    """Модель темы(категория для группы слов)"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название темы"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="URL-идентификатор"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание темы"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        """Автоматически создаем slug из названия с поддержкой кириллицы"""

        if not self.slug:
            self.slug = slugify(self.name, lowercase=True, separator='-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Возвращает URL для просмотра всех слов в этой теме"""

        return reverse("vocabulary:category_detail", args=[self.slug])

    @property
    def word_count(self):
        return self.words.count()


class Word(models.Model):
    """Слово/термин для изучения"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="words",
        verbose_name="Тема"
    )

    term = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Термин (англ.)"
    )

    transcription = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Транскрипция"
    )

    translation_description = models.TextField(
        verbose_name="Описание/перевод на русском"
    )

    image_url = models.URLField(
        blank=True,
        verbose_name="URL изображения"
    )

    audio_url = models.URLField(
        blank=True,
        verbose_name="URL аудио (произношение)"
    )

    # Пример использования в аутентичных предложениях
    example_sentence = models.TextField(
        blank=True,
        verbose_name="Пример использования"
    )

    # Уровень сложности (для фильтрации и SRS)
    DIFFICULTY_CHOICES = [
        (1, "Легкий"),
        (2, "Средний"),
        (3, "Сложный"),
    ]

    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1,
        verbose_name="Уровень сложности"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )

    # Даты (для администрирования)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Слово"
        verbose_name_plural = "Слова"
        ordering = ["term"]  # сортировка по алфавиту
        indexes = [
            models.Index(fields=["term"]),
            models.Index(fields=["category", "difficulty"]),
        ]

    def __str__(self):
        return f"{self.term} ({self.category.name})"

    def get_absolute_url(self):
        return reverse("vocabulary:word_detail", args=[self.pk])

    @property
    def has_image(self):
        """Проверка, есть ли изображение"""
        return bool(self.image_url)

    @property
    def has_audio(self):
        """Проверка, есть ли аудио"""
        return bool(self.audio_url)


class UserWord(models.Model):
    """Словарь пользователя: глобальные слова + свои слова (Premium) с SRS статистикой"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_words",
        verbose_name="Пользователь"
    )

    word = models.ForeignKey(
        "Word",
        on_delete=models.CASCADE,
        related_name="user_words",
        verbose_name="Слово",
        null = True,
        blank = True
    )

    # SRS поля
    stage = models.IntegerField(
        default=0,
        verbose_name="Этап повторения",
        help_text="0=новое, 1=1день, 2=3дня, 3=7дней, 4=14дней, 5=30дней"
    )

    next_review_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата следующего повторения"
    )

    last_reviewed = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата последнего повторения"
    )

    times_reviewed = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество повторений"
    )

    # Мягкое удаление (только для Premium)
    is_deleted_by_user = models.BooleanField(
        default=False,
        verbose_name="Скрыто пользователем"
    )

    # Флаг "выучено навсегда" (опционально)
    is_learned = models.BooleanField(
        default=False,
        verbose_name="Полностью выучено"
    )

    # Даты
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    # СВОИ СЛОВА (только для Premium)
    custom_term = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Свой термин"
    )
    custom_transcription = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Транскрипция"
    )
    custom_description = models.TextField(
        blank=True,
        verbose_name="Описание/перевод"
    )
    custom_image = models.ImageField(
        upload_to="user_words/",
        blank=True,
        null=True,
        verbose_name="Изображение"
    )

    @property
    def display_term(self):
        """Возвращает термин (глобальный или свой)"""
        if self.custom_term:
            return self.custom_term
        return self.word.term if self.word else ""

    @property
    def display_description(self):
        """Возвращает описание (глобальное или своё)"""
        if self.custom_description:
            return self.custom_description
        return self.word.translation_description if self.word else ""

    @property
    def display_transcription(self):
        """Возвращает транскрипцию (глобальную или свою)"""
        if self.custom_transcription:
            return self.custom_transcription
        return self.word.transcription if self.word else ""

    @property
    def display_image(self):
        """Возвращает изображение (своё или глобальное)"""
        if self.custom_image:
            return self.custom_image.url
        return self.word.image_url if self.word and self.word.image_url else ""

    class Meta:
        verbose_name = "Слово пользователя"
        verbose_name_plural = "Слова пользователей"
        # Один пользователь — одно слово
        constraints = [
            models.UniqueConstraint(fields=["user", "word"], name="unique_user_word")
        ]
        # unique_together = ["user", "word"]
        ordering = ["next_review_date"]
        indexes = [
            models.Index(fields=["user", "next_review_date"]),
            models.Index(fields=["user", "stage"]),
        ]

    def __str__(self):
        status = "скрыто" if self.is_deleted_by_user else f"этап {self.stage}"
        term = self.display_term
        return f"{self.user.username} — {term} ({status})"

    def update_stage(self, is_correct):
        """
        Обновляет этап повторения в зависимости от правильности ответа.
        Вызывается после каждой проверки слова.
        """
        intervals = {0: 0, 1: 1, 2: 3, 3: 7, 4: 14, 5: 30}

        if is_correct:
            # Успешно: повышаем stage (максимум 5)
            if self.stage < 5:
                self.stage += 1
        else:
            # Неуспешно: сбрасываем на 0
            self.stage = 0

        # Обновляем счётчик повторений
        self.times_reviewed += 1
        self.last_reviewed = timezone.now()

        # Рассчитываем следующую дату повторения
        days = intervals.get(self.stage, 30)
        if days == 0:
            self.next_review_date = timezone.now()
        else:
            self.next_review_date = timezone.now() + timedelta(days=days)

        # Если stage достиг 5, можно отметить как выученное
        if self.stage >= 5:
            self.is_learned = True

        self.save()

    def hide_for_premium(self):
        """Скрыть слово (только для Premium пользователей)"""

        if self.user.subscription_type == "premium":
            self.is_deleted_by_user = True
            self.save()
            return True
        return False

    def restore_for_premium(self):
        """Восстановить скрытое слово (только для Premium)"""

        if self.user.subscription_type == "premium":
            self.is_deleted_by_user = False
            self.save()
            return True
        return False

    @property
    def needs_review(self):
        """Проверка, нужно ли повторить слово сегодня"""

        if self.is_deleted_by_user:
            return False
        return self.next_review_date <= timezone.now()

    @property
    def is_new(self):
        """Проверка, является ли слово новым"""

        return self.stage == 0 and self.times_reviewed == 0

    @property
    def days_until_review(self):
        """Возвращает количество дней до следующего повторения"""

        if self.needs_review:
            return 0
        delta = self.next_review_date - timezone.now()
        return max(delta.days, 0)

    @classmethod
    def get_review_session(cls, user, limit=3):
        """Возвращает список слов для текущей сессии повторения"""

        words = cls.objects.filter(
            user=user,
            is_deleted_by_user=False,
            next_review_date__lte=timezone.now()
        ).select_related("word", "word__category")[:limit]
        return list(words)
