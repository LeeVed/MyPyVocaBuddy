from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "subscription_type", "city", "country")
    list_filter = ("role", "subscription_type", "city", "country")
    search_fields = ("username", "email", "city", "country")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Подписка и права", {"fields": ("role", "subscription_type")}),
        ("Языковые настройки", {"fields": ("preferred_language", "language_level")}),
        ("Профиль пользователя", {
            "fields": ("avatar", "city", "country", "bio"),
            "classes": ("collapse",)
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide"),
            "fields": ("username", "password1", "password2", "role", "subscription_type"),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Модератор не может редактировать поля "role" и "subscription_type"
        у других пользователей.
        """
        if request.user.role == "moderator" and obj and obj != request.user:
            # Возвращаем кортеж полей, которые станут только для чтения
            return ("role", "subscription_type", "is_staff", "is_superuser")
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Модератор не может удалять пользователей.
        """
        if request.user.role == "moderator":
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """
        Модератор может редактировать пользователей,
        но с ограничениями из get_readonly_fields.
        """
        if request.user.role == "moderator":
            return True
        return super().has_change_permission(request, obj)
