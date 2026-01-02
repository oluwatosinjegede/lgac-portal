from django.urls import path
from apps.applications import views_lga

app_name = "lga"

urlpatterns = [
    path("dashboard/", views_lga.lga_dashboard, name="dashboard"),
    path("review/<int:pk>/", views_lga.lga_review_application, name="review"),
]
