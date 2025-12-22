from django.shortcuts import render, get_object_or_404

from apps.applications.models import Application


# =====================================================
# PUBLIC HOME PAGE
# =====================================================
def home(request):
    """
    Public landing page
    """
    return render(request, "core/home.html")


# =====================================================
# PUBLIC CERTIFICATE VERIFICATION
# =====================================================
def verify_certificate(request, hash_value):
    """
    Public certificate verification endpoint.

    • No authentication required
    • Read-only
    • Verifies only APPROVED certificates
    """

    application = get_object_or_404(
        Application,
        certificate_hash=hash_value,
        status=Application.STATUS_APPROVED,
    )

    return render(
        request,
        "core/verify_certificate.html",
        {
            "application": application,
        },
    )
