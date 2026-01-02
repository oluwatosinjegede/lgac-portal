import uuid
import hmac
import hashlib
import json
import requests

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.permissions import citizen_required
from .models import Payment
from apps.applications.models import Application


# =====================================================
# INITIATE PAYMENT (CITIZEN ONLY)
# =====================================================
@login_required
@citizen_required
def initiate_payment(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id,
        applicant=request.user,
    )

    # -------------------------------------------------
    # STATUS GUARD
    # -------------------------------------------------
    if application.status not in (
        Application.STATUS_SUBMITTED,
        Application.STATUS_PAID,
    ):
        messages.error(
            request,
            "Payment cannot be initiated for this application."
        )
        return redirect("applications:view", application.id)

    # -------------------------------------------------
    # PREVENT DOUBLE PAYMENT
    # -------------------------------------------------
    if hasattr(application, "payment") and (
        application.payment.status == Payment.STATUS_SUCCESS
    ):
        messages.info(
            request,
            "This application has already been paid for."
        )
        return redirect("applications:view", application.id)

    # -------------------------------------------------
    # EMAIL GUARD (PAYSTACK REQUIRES EMAIL)
    # -------------------------------------------------
    if not request.user.email:
        messages.error(
            request,
            "A valid email address is required to make payment."
        )
        return redirect("applications:view", application.id)

    # -------------------------------------------------
    # CREATE / REFRESH PAYMENT
    # -------------------------------------------------
    amount = 5000 * 100  # ₦5,000 → kobo
    reference = f"LGAC-{uuid.uuid4().hex}"

    payment, _ = Payment.objects.update_or_create(
        application=application,
        defaults={
            "reference": reference,
            "amount": amount,
            "status": Payment.STATUS_PENDING,
        },
    )

    # -------------------------------------------------
    # PAYSTACK INITIALIZATION
    # -------------------------------------------------
    payload = {
        "email": request.user.email,
        "amount": amount,
        "reference": reference,
        "callback_url": request.build_absolute_uri(
            reverse("payments:verify")
        ),
        "metadata": {
            "application_id": application.id,
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        settings.PAYSTACK_INIT_URL,
        json=payload,
        headers=headers,
        timeout=15,
    )

    data = response.json()

    # -------------------------------------------------
    # HARD FAILURE HANDLING
    # -------------------------------------------------
    if not data.get("status"):
        payment.status = Payment.STATUS_FAILED
        payment.gateway_response = data
        payment.save(update_fields=["status", "gateway_response"])

        messages.error(
            request,
            f"Payment initialization failed: "
            f"{data.get('message', 'Unknown error')}"
        )
        return redirect("applications:view", application.id)

    # -------------------------------------------------
    # REDIRECT TO PAYSTACK CHECKOUT
    # -------------------------------------------------
    return redirect(data["data"]["authorization_url"])


# =====================================================
# VERIFY PAYMENT (CALLBACK — CITIZEN)
# =====================================================
@login_required
@citizen_required
def verify_payment(request):
    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "Missing payment reference.")
        return redirect("applications:dashboard")

    payment = get_object_or_404(Payment, reference=reference)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        f"{settings.PAYSTACK_VERIFY_URL}{reference}",
        headers=headers,
        timeout=10,
    )

    data = response.json()
    payment.gateway_response = data

    # -------------------------------------------------
    # VERIFY RESULT
    # -------------------------------------------------
    if data.get("data", {}).get("status") == "success":
        payment.status = Payment.STATUS_SUCCESS
        payment.paid_at = timezone.now()

        application = payment.application
        application.status = Application.STATUS_PAID
        application.save(update_fields=["status"])

        messages.success(request, "Payment successful.")
    else:
        payment.status = Payment.STATUS_FAILED
        messages.error(
            request,
            "Payment failed or was cancelled."
        )

    payment.save(
        update_fields=["status", "paid_at", "gateway_response"]
    )
    return redirect("applications:dashboard")


# =====================================================
# PAYSTACK WEBHOOK (PUBLIC)
# =====================================================
@csrf_exempt
def paystack_webhook(request):
    signature = request.headers.get("x-paystack-signature")
    body = request.body

    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()

    if signature != expected_signature:
        return HttpResponse(status=400)

    payload = json.loads(body)

    if payload.get("event") == "charge.success":
        data = payload["data"]
        reference = data["reference"]

        try:
            payment = Payment.objects.select_for_update().get(
                reference=reference
            )
        except Payment.DoesNotExist:
            return HttpResponse(status=200)

        if payment.status == Payment.STATUS_SUCCESS:
            return HttpResponse(status=200)  # idempotent

        payment.status = Payment.STATUS_SUCCESS
        payment.paid_at = timezone.now()
        payment.gateway_response = payload
        payment.save()

        application = payment.application
        application.status = Application.STATUS_PAID
        application.save(update_fields=["status"])

    return HttpResponse(status=200)


# =====================================================
# PAYMENT RECEIPT (CITIZEN ONLY)
# =====================================================
@login_required
@citizen_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        status=Payment.STATUS_SUCCESS,
        application__applicant=request.user,
    )

    return render(
        request,
        "payments/receipt.html",
        {"payment": payment},
    )
