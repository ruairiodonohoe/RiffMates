"""
URL configuration for RiffMates project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ninja import NinjaAPI

from home.api import router as home_router
from promoters.api import router as promoters_router
from bands.api import router as bands_router

api = NinjaAPI(version="1.0")
api.add_router("/home/", home_router)
api.add_router("/promoters/", promoters_router)
api.add_router("/bands/", bands_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("home.urls")),
    path("bands/", include("bands.urls")),
    path("content/", include("content.urls")),
    path("api/v1/", api.urls),
    path("promoters/", include("promoters.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
