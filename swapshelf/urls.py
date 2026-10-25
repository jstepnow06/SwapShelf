from pathlib import Path

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.static import serve
from django.urls import include, path
from django.urls import re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {"document_root": Path(settings.BASE_DIR) / "market" / "static"},
    ),
    path("", include("market.urls")),
]
