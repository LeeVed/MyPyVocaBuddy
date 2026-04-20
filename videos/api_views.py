from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Video
from .serializers import VideoSerializer
from .filters import VideoFilter


class VideoListAPIView(ListAPIView):
    """API для списка видео с фильтрацией (демонстрация django-filter)"""
    queryset = Video.objects.filter(is_active=True)
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VideoFilter
    