from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Video
from vocabulary.models import UserWord


@login_required
def video_list(request):
    """Список видео (видеотека)"""

    # Все активные видео видят все пользователи
    videos = Video.objects.filter(is_active=True)

    # Фильтр по уровню — ТОЛЬКО ДЛЯ PREMIUM
    level_filter = None
    if request.user.subscription_type == "premium":
        level_filter = request.GET.get("level")
        if level_filter and level_filter in ["beginner", "intermediate", "advanced"]:
            videos = videos.filter(level=level_filter)

    # Статистика для фильтров (только для Premium)
    total_count = videos.count()

    context = {
        "videos": videos,
        "level_filter": level_filter,
        "total_count": total_count,
        "is_premium_user": request.user.subscription_type == "premium",
    }
    return render(request, "videos/list.html", context)


@login_required
def video_detail(request, pk):
    """Страница просмотра видео"""

    video = get_object_or_404(Video, pk=pk, is_active=True)

    # Все пользователи могут смотреть любые видео (и бесплатные, и Premium)
    # Premium видео не блокируются, просто у Free нет дополнительных функций

    context = {
        "video": video,
        "is_premium_user": request.user.subscription_type == "premium",
    }
    return render(request, "videos/detail.html", context)


@login_required
@require_POST
def add_words(request, pk):
    """Добавляет слова из видео в словарь пользователя (только для Premium)"""

    if request.user.role != "student":
        return JsonResponse({"error": "Доступ запрещён"}, status=403)

    if request.user.subscription_type != "premium":
        return JsonResponse({"error": "Доступно только для Premium пользователей"}, status=403)

    video = get_object_or_404(Video, pk=pk, is_active=True)

    added_count = 0
    for word in video.words.all():
        user_word, created = UserWord.objects.get_or_create(
            user=request.user,
            word=word,
            defaults={
                "stage": 0,
                "next_review_date": timezone.now(),
            }
        )
        if created:
            added_count += 1

    return JsonResponse({
        "success": True,
        "message": f"Добавлено {added_count} новых слов в ваш словарь!"
    })
