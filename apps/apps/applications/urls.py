from django.urls import path
from . import views
from . import views_lga

app_name = "applications"

urlpatterns = [
    # =============================
    # CITIZEN ROUTES
    # =============================
    path("", views.dashboard, name="dashboard"),
    path("new/", views.new_application, name="new"),
    path("<int:pk>/", views.view_application, name="view"),

    # =============================
    # LGA OFFICER ROUTES
    # =============================
    path("lga/dashboard/", views_lga.lga_dashboard, name="lga_dashboard"),
    path("lga/review/<int:pk>/", views_lga.lga_review_application, name="lga_review"),
    path("<int:pk>/withdraw/", views.withdraw_application, name="withdraw"),
    path("verify/<str:hash_value>/", views.verify_certificate, name="verify_certificate"),

    path("certificate/download/<int:pk>/",views.download_certificate,name="download_certificate",),

]


