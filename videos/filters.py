import django_filters
from .models import Video


class VideoFilter(django_filters.FilterSet):
    """Фильтр для видео """

    level = django_filters.ChoiceFilter(choices=Video.LEVEL_CHOICES)

    class Meta:
        model = Video
        fields = ["level", "is_premium"]
