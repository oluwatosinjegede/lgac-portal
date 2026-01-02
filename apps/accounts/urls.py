from django.urls import path
from . import views
from .views import keep_alive

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_custom, name="logout"),
    path("verify-nin/", views.verify_nin, name="verify_nin"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("lga-assignment/", views.lga_assignment_view, name="lga_assignment"),
    path("profile/", views.profile_view, name="profile"),
    path("ping/", keep_alive, name="keep_alive"),
]
