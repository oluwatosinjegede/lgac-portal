from django.urls import path
from . import views
from .views import lga_dashboard

app_name = "lga"

urlpatterns = [
    path("dashboard/", lga_dashboard, name="dashboard"),
]
