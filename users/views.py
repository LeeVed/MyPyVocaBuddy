from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from vocabulary.utils import add_base_words_to_user


def register(request):
    """Регистрация нового пользователя"""

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Автоматически добавляем базовые слова из БД
            added_words = add_base_words_to_user(user)

            # Автоматически входим после регистрации
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}! 🎉 В ваш словарь добавлено {added_words} слов.")
            return redirect("common:dashboard")

    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.role == "moderator":
            return "/admin/"
        return "/dashboard/"
