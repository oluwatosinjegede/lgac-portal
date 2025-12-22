from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.accounts.permissions import lga_staff_required


# =====================================================
# LGA STAFF DASHBOARD
# =====================================================
@login_required
@lga_staff_required
def lga_dashboard(request):
    """
    LGA Officer Dashboard
    Accessible only to authenticated LGA staff.
    """

    # Super admins must use Django admin
    if getattr(request.user, "is_admin_user", False):
        return redirect("admin:index")

    return render(request, "lga/dashboard.html")

