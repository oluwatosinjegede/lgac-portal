from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.models import User
from django.http import HttpResponseForbidden

@login_required
def dashboard(request):
    print(">>> LGA DASHBOARD VIEW HIT <<<")
    if request.user.role != User.ROLE_LGA_OFFICER:
        return HttpResponseForbidden("You are not allowed to access this page")

    return render(request, "lga/dashboard.html")
