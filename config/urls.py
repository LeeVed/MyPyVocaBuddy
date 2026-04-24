from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from users.api_views import RegisterFCMDeviceView
from common.api_views import (
    CheckPronunciationAPIView,
    CheckWrittenAnswerAPIView,
    HideWordAPIView,
    RestoreWordAPIView,
    CurrentWordAPIView,
    ProcessResultAPIView,
    WordDetailAPIView,
)
from django.views.static import serve
from users.views import CustomLoginView
from videos.api_views import VideoListAPIView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("common.urls")),

    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),

    path("register/", user_views.register, name="register"),
    path("videos/", include("videos.urls")),
    path("premium/", include("premium.urls")),

    # API для флеш-карт
    path("api/review/current-word/", CurrentWordAPIView.as_view(), name="api_current_word"),
    path("api/review/process-result/", ProcessResultAPIView.as_view(), name="api_process_result"),
    path("api/review/word-detail/<int:word_id>/", WordDetailAPIView.as_view(), name="api_word_detail"),

    # API для проверки ответов
    path("api/review/check-pronunciation/", CheckPronunciationAPIView.as_view(), name="api_check_pronunciation"),
    path("api/review/check-written/", CheckWrittenAnswerAPIView.as_view(), name="api_check_written"),

    # API для управления словами
    path("api/words/hide/<int:user_word_id>/", HideWordAPIView.as_view(), name="api_hide_word"),
    path("api/words/restore/<int:user_word_id>/", RestoreWordAPIView.as_view(), name="api_restore_word"),

    # API для приема токенов для отправки push уведомлений
    path("api/register-device/", RegisterFCMDeviceView.as_view(), name="register_fcm_device"),
    # API для видеотеки
    path("api/videos/", VideoListAPIView.as_view(), name="api_video_list"),
]

urlpatterns += [
    path('firebase-messaging-sw.js', serve, {'path': 'firebase-messaging-sw.js', 'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
