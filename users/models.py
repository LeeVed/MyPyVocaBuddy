from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("moderator", "Moderator"),
        ("superuser", "Superuser"),
    ]

    SUBSCRIPTION_CHOICES = [
        ("free", "Free"),
        ("premium","Premium"),
    ]

    LANGUAGE_LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
    ]

    LANGUAGE_CHOICES = [
        ("ru", "Русский"),
        ("en", "English"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default="free")
    # Язык интерфейса — доступен всем (включая незарегистрированных)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="ru")
    # Уровень языка — только для Premium
    language_level = models.CharField(max_length=20, choices=LANGUAGE_LEVEL_CHOICES, null=True, blank=True)

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Город"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Страна"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="О себе"
    )

    def clean(self):
        """Валидация: language_level только для Premium"""
        super().clean()
        if self.subscription_type == "free" and self.language_level is not None:
            raise ValidationError("Language level can only be set for Premium users")

    def save(self, *args, **kwargs):
        """Автоматически сбрасываем language_level при смене подписки на free"""
        if self.pk:
            old_user = CustomUser.objects.get(pk=self.pk)
            if old_user.subscription_type == "premium" and self.subscription_type == "free":
                self.language_level = None
        super().save(*args, **kwargs)

    @property
    def can_set_language_level(self):
        """Проверка, может ли пользователь устанавливать уровень языка"""
        return self.subscription_type == "premium"

    @property
    def get_avatar_url(self):
        """Возвращает URL аватара или ссылку на изображение по умолчанию"""
        if self.avatar:
            return self.avatar.url
        return "/static/images/default-avatar.png"

    def __str__(self):
        return f"{self.username} ({self.get_subscription_type_display()})"
