from django.urls import path

from promoters import views

urlpatterns = [
    path("", views.promoters, name="promoters"),
    path("partial-promoters/", views.partial_promoters, name="partial_promoters"),
]
