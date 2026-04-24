from django.core.management.base import BaseCommand
from videos.models import Video


class Command(BaseCommand):
    help = "Заполняет базу данных короткими видео (5-7 мин) от ведущих IT-специалистов"

    def handle(self, *args, **options):
        videos_data = [
            {
                "title": "Guido van Rossum: The Future of Python",
                "youtube_url": "https://youtu.be/example1",
                "description": "Гвидо ван Россум, создатель Python, рассказывает о будущем языка и философии разработки.",
                "level": "intermediate",
                "is_premium": False,
                "duration": 360,  # 6 минут
                "speaker": "Guido van Rossum",
                "topic": "Python Future",
            },
            {
                "title": "Linus Torvalds: Git and Open Source",
                "youtube_url": "https://youtu.be/example2",
                "description": "Линус Торвальдс о создании Git, открытом коде и управлении большими проектами.",
                "level": "advanced",
                "is_premium": False,
                "duration": 420,  # 7 минут
                "speaker": "Linus Torvalds",
                "topic": "Open Source",
            },
            {
                "title": "Elon Musk: Engineering & Innovation",
                "youtube_url": "https://youtu.be/example3",
                "description": "Илон Маск о подходе к инжинирингу, решении сложных задач и инновациях.",
                "level": "intermediate",
                "is_premium": True,
                "duration": 300,  # 5 минут
                "speaker": "Elon Musk",
                "topic": "Innovation",
            },
            {
                "title": "Brendan Eich: JavaScript Creation Story",
                "youtube_url": "https://youtu.be/example4",
                "description": "Брендан Айх, создатель JavaScript, рассказывает историю создания языка за 10 дней.",
                "level": "intermediate",
                "is_premium": False,
                "duration": 380,  # 6 минут 20 секунд
                "speaker": "Brendan Eich",
                "topic": "JavaScript History",
            },
            {
                "title": "Dennis Ritchie: Unix Legacy",
                "youtube_url": "https://youtu.be/example5",
                "description": "Деннис Ритчи (архивное интервью) о создании Unix и языке C.",
                "level": "advanced",
                "is_premium": True,
                "duration": 410,  # 6 минут 50 секунд
                "speaker": "Dennis Ritchie",
                "topic": "Unix History",
            },
            {
                "title": "Satya Nadella: AI and Cloud Computing",
                "youtube_url": "https://youtu.be/example6",
                "description": "Сатья Наделла, CEO Microsoft, об искусственном интеллекте и облачных технологиях.",
                "level": "beginner",
                "is_premium": False,
                "duration": 350,  # 5 минут 50 секунд
                "speaker": "Satya Nadella",
                "topic": "AI & Cloud",
            },
            {
                "title": "Margaret Hamilton: Apollo Software Engineering",
                "youtube_url": "https://youtu.be/example7",
                "description": "Маргарет Гамильтон о разработке ПО для Apollo 11 и важности тестирования.",
                "level": "intermediate",
                "is_premium": True,
                "duration": 390,  # 6 минут 30 секунд
                "speaker": "Margaret Hamilton",
                "topic": "Software Engineering",
            },
        ]

        created_count = 0
        for video_data in videos_data:
            video, created = Video.objects.get_or_create(
                title=video_data["title"],
                defaults={
                    "youtube_url": video_data["youtube_url"],
                    "description": video_data["description"],
                    "level": video_data["level"],
                    "is_premium": video_data["is_premium"],
                    "duration": video_data["duration"],
                },
            )
            if created:
                created_count += 1
                premium_mark = "Premium" if video.is_premium else ""
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Добавлено видео: {video.title} ({video.duration} сек){premium_mark}"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"\nГотово! Добавлено новых видео: {created_count}"))
