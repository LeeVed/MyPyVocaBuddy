from django.shortcuts import render

def premium_info(request):
    """Страница информации о Premium подписке"""

    return render(request, "premium/info.html")