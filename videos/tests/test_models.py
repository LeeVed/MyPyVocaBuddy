from videos.models import Video
import time


class TestVideo:
    """Тесты для модели Video"""

    def test_create_video(self, video):
        """Создание видео"""

        assert video.title == "Python Variables Tutorial"
        assert video.level == "beginner"
        assert video.is_premium is False
        assert video.is_active is True
        assert video.duration == 366
        assert str(video) == "Python Variables Tutorial"

    def test_level_choices(self, db):
        """Проверка выбора уровня сложности"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://youtube.com/test",
            level="intermediate"
        )
        assert video.get_level_display() == "Средний"

    def test_words_many_to_many(self, video, word, second_word):
        """Связь многие-ко-многим со словами"""

        assert video.words.count() == 2
        assert word in video.words.all()
        assert second_word in video.words.all()

    def test_youtube_embed_url_standard(self, db):
        """Преобразование стандартной YouTube ссылки"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://www.youtube.com/watch?v=abc123",
            level="beginner"
        )
        assert video.youtube_embed_url == "https://www.youtube.com/embed/abc123"

    def test_youtube_embed_url_with_params(self, db):
        """Преобразование YouTube ссылки с дополнительными параметрами"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://www.youtube.com/watch?v=abc123&t=10s",
            level="beginner"
        )
        assert video.youtube_embed_url == "https://www.youtube.com/embed/abc123"

    def test_youtube_embed_url_youtu_be(self, db):
        """Преобразование короткой ссылки youtu.be"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://youtu.be/xyz789",
            level="beginner"
        )
        assert video.youtube_embed_url == "https://www.youtube.com/embed/xyz789"

    def test_youtube_embed_url_unknown_format(self, db):
        """Неизвестный формат возвращает оригинальный URL"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://example.com/video",
            level="beginner"
        )
        assert video.youtube_embed_url == "https://example.com/video"

    def test_duration_minutes(self, video):
        """Форматирование длительности в минуты и секунды"""

        assert video.duration_minutes == "6 мин 6 сек"

    def test_duration_minutes_none(self, db):
        """Длительность не указана"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://youtube.com/test",
            level="beginner",
            duration=None
        )
        assert video.duration_minutes == "—"

    def test_duration_minutes_exact_minute(self, db):
        """Ровно 5 минут"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://youtube.com/test",
            level="beginner",
            duration=300
        )
        assert video.duration_minutes == "5 мин 0 сек"

    def test_get_absolute_url(self, video):
        """URL для детального просмотра видео"""

        url = video.get_absolute_url()
        assert url == f"/videos/{video.pk}/"

    def test_ordering(self, db):
        """Видео сортируются по дате создания (новые сначала)"""
         # Очищаем все видео
        Video.objects.all().delete()

        # Создаём старое видео
        old_video = Video.objects.create(
            title="Old Video",
            youtube_url="https://youtube.com/old",
            level="beginner"
        )

        # Небольшая задержка для гарантии разницы во времени
        time.sleep(0.1)

        # Создаём новое видео
        new_video = Video.objects.create(
            title="New Video",
            youtube_url="https://youtube.com/new",
            level="beginner"
        )

        videos = Video.objects.filter(is_active=True)

        # Новое видео должно быть первым (сортировка по -created_at)
        assert videos[0] == new_video
        assert videos[1] == old_video

    def test_inactive_video_not_in_default_queryset(self, inactive_video, video):
        """Неактивные видео не отображаются по умолчанию"""

        active_videos = Video.objects.filter(is_active=True)
        assert video in active_videos
        assert inactive_video not in active_videos

    def test_speaker_field(self, db):
        """Поле speaker"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://youtube.com/test",
            level="beginner",
            speaker="Corey Schafer"
        )
        assert video.speaker == "Corey Schafer"

    def test_topic_field(self, db):
        """Поле topic"""

        video = Video.objects.create(
            title="Test",
            youtube_url="https://youtube.com/test",
            level="beginner",
            topic="Python Basics"
        )
        assert video.topic == "Python Basics"
