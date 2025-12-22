from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("verify/<str:hash_value>/", views.verify_certificate, name="verify_certificate"),
]
