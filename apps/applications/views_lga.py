from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.accounts.permissions import lga_staff_required
from apps.applications.models import Application
from apps.core.utils import generate_certificate_pdf


# =====================================================
# INTERNAL HELPER
# =====================================================
def _get_assigned_lga_or_redirect(request):
    """
    Ensure LGA officer has an assigned LGA
    """
    if not request.user.lga:
        messages.error(
            request,
            "No Local Government Area is assigned to your account. "
            "Please contact the system administrator."
        )
        return None
    return request.user.lga


# =====================================================
# LGA OFFICER DASHBOARD
# =====================================================
@login_required
@lga_staff_required
def lga_dashboard(request):
    """
    LGA Officer Dashboard
    """

    # Admins must use admin interface
    if request.user.is_admin_user:
        return redirect("/admin/")

    officer_lga = _get_assigned_lga_or_redirect(request)
    if not officer_lga:
        return redirect("/")

    applications = (
        Application.objects
        .filter(
            lga=officer_lga,
            status__in=[
                Application.STATUS_PAID,
                Application.STATUS_IN_REVIEW,
            ],
        )
        .select_related("applicant", "lga")
        .order_by("-created_at")
    )

    return render(
        request,
        "lga/dashboard.html",
        {
            "applications": applications,
            "lga": officer_lga,
        },
    )


# =====================================================
# REVIEW / APPROVE / REJECT
# =====================================================
@login_required
@lga_staff_required
def lga_review_application(request, pk):
    """
    LGA Officer reviews an application
    """

    if request.user.is_admin_user:
        return redirect("/admin/")

    officer_lga = _get_assigned_lga_or_redirect(request)
    if not officer_lga:
        return redirect("/")

    application = get_object_or_404(
        Application,
        pk=pk,
        lga=officer_lga,
        status__in=[
            Application.STATUS_PAID,
            Application.STATUS_IN_REVIEW,
        ],
    )

    # AUTO-TRANSITION: PAID → IN_REVIEW
    if request.method == "GET" and application.status == Application.STATUS_PAID:
        application.status = Application.STATUS_IN_REVIEW
        application.save(update_fields=["status"])

    if request.method == "POST":
        action = request.POST.get("action")
        notes = request.POST.get("notes", "").strip()

        application.approver_notes = notes

        if action == "approve":
            application.status = Application.STATUS_APPROVED
            application.approved_at = timezone.now()

            pdf_path, cert_hash = generate_certificate_pdf(application)
            application.certificate_pdf = pdf_path
            application.certificate_hash = cert_hash

            messages.success(
                request,
                "Application approved and certificate issued."
            )

        elif action == "reject":
            application.status = Application.STATUS_REJECTED
            messages.warning(request, "Application rejected.")

        else:
            application.status = Application.STATUS_IN_REVIEW
            messages.info(request, "Application marked as in review.")

        application.save()
        return redirect("applications:lga_dashboard")

    return render(
        request,
        "lga/review_application.html",
        {"app": application},
    )
