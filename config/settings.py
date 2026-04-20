import os
from pathlib import Path
from dotenv import load_dotenv
from celery.schedules import crontab


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


import firebase_admin
from firebase_admin import credentials

FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""))

if FIREBASE_CREDENTIALS and os.path.exists(FIREBASE_CREDENTIALS):
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # сторонние
    "bootstrap5",
    "rest_framework",
    "django_celery_beat",
    "fcm_django", # для push уведомлений
    "django_filters",
    # свои
    "common",
    "users",
    "vocabulary",
    "videos",
    "premium",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

LANGUAGE_CODE = "en-us"

LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
]

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
# STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.CustomUser"

# перенаправлять после входа
LOGIN_REDIRECT_URL = "common:dashboard"
LOGOUT_REDIRECT_URL = "common:home"
# перенаправлять неавторизованных пользователей
LOGIN_URL = "login"

# Адрес брокера сообщений (Redis)
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379")
# Форматы данных
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
# Часовые пояса для Celery (для периодических задач)
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
# Настройки для django-celery-beat
DJANGO_CELERY_BEAT_TZ_AWARE = False

CELERY_TASK_TRACK_STARTED = os.getenv("CELERY_TASK_TRACK_STARTED", "True") == "True"
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", 1800))

# Настройки FCM-DJANGO
FCM_DJANGO_SETTINGS = {
    "DEFAULT_FIREBASE_APP": None,
    "ONE_DEVICE_PER_USER": True,
    "DELETE_INACTIVE_DEVICES": True,
}

# Путь к папке с переводами
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# CSRF для работы через nginx
CSRF_TRUSTED_ORIGINS = [
    f"http://{host}" for host in ALLOWED_HOSTS
] + [
    f"https://{host}" for host in ALLOWED_HOSTS
]
