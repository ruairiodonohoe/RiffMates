from django.urls import path

from bands import views

urlpatterns = [
    # Musicians
    path("musicians/", views.musicians, name="musicians"),
    path("musician/<int:musician_id>/", views.musician, name="musician"),
    path("musician/add/", views.edit_musician, name="add_musician"),
    path("musician/<int:musician_id>/edit/", views.edit_musician, name="edit_musician"),
    # Bands
    path("band/<int:band_id>/", views.band, name="band"),
    path("bands/", views.bands, name="bands"),
    # Venues
    path("venues/", views.venues, name="venues"),
    path("venue/add/", views.edit_venue, name="add_venue"),
    path("venue/<int:venue_id>/edit/", views.edit_venue, name="edit_venue"),
    # Restricted
    path("restricted_page/", views.restricted_page, name="restricted_page"),
    path(
        "musician_restricted/<int:musician_id>/",
        views.musician_restricted,
        name="musician_restricted",
    ),
]
