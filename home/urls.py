from django.urls import path

from home import views

urlpatterns = [
    path("", views.home, name="home"),
    path("credits/", views.credits, name="credits"),
    path("about/", views.about),
    path("version_info/", views.version_info),
    path("news/", views.news, name="news"),
    path("news-adv", views.news_advanced, name="news_advanced"),
]
