from django.urls import path
from . import views

app_name = "common"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("review/", views.review, name="review"),
    path("words/", views.word_list, name="word_list"),
    path('words/add/', views.add_custom_word, name='add_custom_word'),
    path("premium/info/", views.premium_info, name="premium_info"),
]
