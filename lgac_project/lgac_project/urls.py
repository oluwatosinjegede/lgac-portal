from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.applications import views as application_views

urlpatterns = [
    path("", include("apps.core.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("applications/", include("apps.applications.urls")),
    path("payments/", include("apps.payments.urls")),
    path("lga/", include("apps.lga.urls")),

    # 🔐 Certificate verification (public)
    path(
        "verify/<str:hash_value>/",
        application_views.verify_certificate,
        name="verify_certificate",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
