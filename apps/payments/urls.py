from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("initiate/<int:application_id>/", views.initiate_payment, name="initiate"),
    path("verify/", views.verify_payment, name="verify"),
    path("receipt/<int:payment_id>/", views.payment_receipt, name="receipt"),
    path("webhook/paystack/", views.paystack_webhook, name="webhook"),
]
