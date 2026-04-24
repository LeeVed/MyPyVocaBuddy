from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from vocabulary.models import UserWord, Category
from django.contrib import messages
from vocabulary.forms import CustomWordForm


def home(request):
    """Главная страница (лендинг)"""
    return render(request, "common/home.html")


@login_required
def dashboard(request):
    """Личный кабинет пользователя со статистикой и фильтром по темам только для студентов"""

    if request.user.role != "student":
        return redirect("/admin/")

    selected_category_slug = request.GET.get("category")

    user_words = UserWord.objects.filter(
        user=request.user,
        is_deleted_by_user=False
    )

    if selected_category_slug:
        user_words = user_words.filter(word__category__slug=selected_category_slug)

    total_words = user_words.count()
    new_words = user_words.filter(stage=0).count()
    to_review = user_words.filter(next_review_date__lte=timezone.now()).count()
    learned_words = user_words.filter(stage__gte=5).count()

    categories = Category.objects.all()

    selected_category_name = None
    if selected_category_slug:
        try:
            selected_category = Category.objects.get(slug=selected_category_slug)
            selected_category_name = selected_category.name
        except Category.DoesNotExist:
            pass

    context = {
        "total_words": total_words,
        "new_words": new_words,
        "to_review": to_review,
        "learned_words": learned_words,
        "categories": categories,
        "selected_category_slug": selected_category_slug,
        "selected_category_name": selected_category_name,
    }
    return render(request, "common/dashboard.html", context)


@login_required
def review(request):
    """Страница повторения слов (флеш-карты)"""

    if request.user.role != "student":
        return redirect("/admin/")

    # Получаем слова для повторения (сессия до 3 слов)
    session_words = UserWord.get_review_session(request.user, limit=3)

    if not session_words:
        return render(request, "common/review_empty.html")

    # Сохраняем сессию как ОЧЕРЕДЬ (список слов, которые нужно обработать)
    request.session["review_queue"] = [w.id for w in session_words]
    request.session["review_mode"] = "show"  # show, write, speak
    request.session["failed_words"] = []  # слова, которые нужно повторить позже

    context = {
        "user_word": session_words[0],
        "total_count": len(session_words),
        "current_index": 1,
    }
    return render(request, "common/review.html", context)


@login_required
def word_list(request):
    """Список слов пользователя только для студентов"""

    if request.user.role != "student":
        return redirect("/admin/")

    selected_category_slug = request.GET.get("category")
    filter_status = request.GET.get("status")  # all, new, review, learned, hidden

    # Базовый queryset (все слова пользователя)
    user_words = UserWord.objects.filter(user=request.user).select_related("word", "word__category")

    # Фильтрация по теме (только для глобальных слов)
    if selected_category_slug:
        user_words = user_words.filter(word__category__slug=selected_category_slug)

    # Подсчёт скрытых слов (для карточки статистики)
    hidden_count = UserWord.objects.filter(user=request.user, is_deleted_by_user=True).count()

    # Фильтрация по статусу
    if filter_status == "new":
        user_words = user_words.filter(stage=0, times_reviewed=0, is_deleted_by_user=False)
    elif filter_status == "review":
        user_words = user_words.filter(next_review_date__lte=timezone.now(), is_deleted_by_user=False)
    elif filter_status == "learned":
        user_words = user_words.filter(stage__gte=5, is_deleted_by_user=False)
    elif filter_status == "hidden":
        user_words = user_words.filter(is_deleted_by_user=True)
    else:
        filter_status = "all"
        user_words = user_words.filter(is_deleted_by_user=False)

    # Все темы для фильтра
    categories = Category.objects.all()

    # Статистика для карточек
    total_count = UserWord.objects.filter(user=request.user, is_deleted_by_user=False).count()
    new_count = UserWord.objects.filter(user=request.user, is_deleted_by_user=False, stage=0, times_reviewed=0).count()
    review_count = UserWord.objects.filter(
        user=request.user,
        is_deleted_by_user=False,
        next_review_date__lte=timezone.now()
    ).count()
    learned_count = UserWord.objects.filter(user=request.user, is_deleted_by_user=False, stage__gte=5).count()

    context = {
        "user_words": user_words,
        "categories": categories,
        "selected_category_slug": selected_category_slug,
        "filter_status": filter_status,
        "total_count": total_count,
        "new_count": new_count,
        "review_count": review_count,
        "learned_count": learned_count,
        "hidden_count": hidden_count,
    }
    return render(request, "common/word_list.html", context)


@login_required
def premium_info(request):
    """Страница информации о Premium подписке только для студентов"""
    if request.user.role != "student":
        return redirect("/admin/")
    return render(request, "premium/info.html")


@login_required
def add_custom_word(request):
    """Добавление своего слова только для Premium студентов"""

    # Проверка: только студент и только Premium
    if request.user.role != "student":
        return redirect("/admin/")

    if request.user.subscription_type != "premium":
        messages.error(request, "Эта функция доступна только Premium пользователям")
        return redirect("common:dashboard")

    if request.method == "POST":
        form = CustomWordForm(request.POST, request.FILES)
        if form.is_valid():
            user_word = form.save(request.user)
            messages.success(request, f"Слово '{user_word.display_term}' добавлено в ваш словарь!")
            return redirect('common:word_list')
    else:
        form = CustomWordForm()

    return render(request, "common/add_custom_word.html", {"form": form})
