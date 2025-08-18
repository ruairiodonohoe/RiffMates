from django.urls import path


from content import views

urlpatterns = [
    path("comment/", views.comment, name="comment"),
    path("comment-accepted/", views.comment_accepted, name="comment_accepted"),
    path("list-ads/", views.list_ads, name="list_ads"),
    path("seeking-ad/", views.seeking_ad, name="seeking_ad"),
    path("edit-seeking-ad/<int:ad_id>", views.seeking_ad, name="edit_seeking_ad"),
]
