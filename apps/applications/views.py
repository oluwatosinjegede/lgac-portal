from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.conf import settings

from apps.accounts.permissions import citizen_required

from .forms import ApplicationForm
from .models import Application

import os


# =====================================================
# CITIZEN DASHBOARD
# =====================================================
@login_required
@citizen_required
def dashboard(request):
    """
    Citizen dashboard – list ONLY own applications
    """
    applications = (
        Application.objects
        .filter(applicant=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "applications/dashboard.html",
        {"applications": applications},
    )


# =====================================================
# NEW APPLICATION (CITIZEN ONLY)
# =====================================================
@login_required
@citizen_required
def new_application(request):
    """
    Create new LGAC application
    """
    if request.method == "POST":
        form = ApplicationForm(
            data=request.POST,
            files=request.FILES,
            user=request.user,
        )

        if form.is_valid():
            application = form.save(commit=False)

            # OWNERSHIP & STATUS
            application.applicant = request.user
            application.status = Application.STATUS_SUBMITTED

            # SNAPSHOT IDENTITY (IMMUTABLE)
            application.full_name = request.user.full_name
            application.email = request.user.email
            application.phone = request.user.phone
            application.nin = request.user.nin

            if not application.lga:
                messages.error(
                    request,
                    "Local Government selection is required."
                )
                return redirect("applications:new")

            application.save()

            messages.success(
                request,
                "Application submitted successfully. Proceed to payment."
            )

            return redirect(
                "payments:initiate",
                application_id=application.id,
            )
    else:
        form = ApplicationForm(user=request.user)

    return render(
        request,
        "applications/new_application.html",
        {"form": form},
    )


# =====================================================
# VIEW APPLICATION (CITIZEN ONLY)
# =====================================================
@login_required
@citizen_required
def view_application(request, pk):
    application = get_object_or_404(
        Application,
        pk=pk,
        applicant=request.user,
    )

    return render(
        request,
        "applications/view.html",
        {"app": application},
    )


# =====================================================
# DOWNLOAD CERTIFICATE (CITIZEN ONLY)
# =====================================================
@login_required
@citizen_required
def download_certificate(request, pk):
    application = get_object_or_404(
        Application,
        pk=pk,
        applicant=request.user,
        status=Application.STATUS_APPROVED,
    )

    if not application.certificate_hash:
        raise Http404("Certificate not available")

    filename = f"lgac_{application.id}_{application.certificate_hash[:12]}.pdf"
    file_path = os.path.join(
        settings.MEDIA_ROOT,
        "certificates",
        filename,
    )

    if not os.path.exists(file_path):
        raise Http404("Certificate file missing")

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )


# =====================================================
# WITHDRAW APPLICATION (CITIZEN ONLY)
# =====================================================
@login_required
@citizen_required
def withdraw_application(request, pk):
    application = get_object_or_404(
        Application,
        pk=pk,
        applicant=request.user,
    )

    if application.status not in (
        Application.STATUS_PAID,
        Application.STATUS_IN_REVIEW,
    ):
        messages.error(
            request,
            "This application can no longer be withdrawn."
        )
        return redirect("applications:dashboard")

    if request.method == "POST":
        application.status = Application.STATUS_WITHDRAWN
        application.save(update_fields=["status"])

        messages.success(
            request,
            "Your application has been successfully withdrawn."
        )
        return redirect("applications:dashboard")

    return render(
        request,
        "applications/confirm_withdraw.html",
        {"app": application},
    )


# =====================================================
# PUBLIC CERTIFICATE VERIFICATION
# =====================================================
def verify_certificate(request, hash_value):
    application = get_object_or_404(
        Application,
        certificate_hash=hash_value,
        status=Application.STATUS_APPROVED,
    )

    return render(
        request,
        "applications/verify.html",
        {"application": application},
    )
