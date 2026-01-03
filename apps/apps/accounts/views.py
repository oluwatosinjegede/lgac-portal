from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse, NoReverseMatch
from django.http import JsonResponse

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

from .forms import SignupForm, LGAOfficerAssignmentForm
from .models import User
from apps.accounts.permissions import lga_officer_required

import json
import re
import requests



# =====================================================
# SIGN UP (PUBLIC — CITIZEN ONLY)
# =====================================================
def signup_view(request):
    """
    Citizen signup.
    NIN verification is enforced at form level via session.
    """

    if request.method == "POST":
        # IMPORTANT: pass request into form
        form = SignupForm(
            request.POST,
            initial={"request": request},
        )

        if form.is_valid():
            form.save()

            # Cleanup verification session
            request.session.pop("nin_verified", None)
            request.session.pop("verified_nin", None)

            messages.success(
                request,
                "Account created successfully. Please log in."
            )
            return redirect(reverse("accounts:login"))
    else:
        form = SignupForm(initial={"request": request})

    return render(request, "accounts/signup.html", {"form": form})


# =====================================================
# NIN VERIFICATION (AJAX ENDPOINT)
# =====================================================
@csrf_exempt
@require_POST
def verify_nin(request):
    """
    Verify National Identification Number (NIN)
    Accepts JSON or form-encoded POST.
    Sets session flags on success.
    """

    # ----------------------------------
    # Extract NIN (JSON or form POST)
    # ----------------------------------
    nin = None

    if request.content_type and request.content_type.startswith("application/json"):
        try:
            payload = json.loads(request.body.decode("utf-8"))
            nin = payload.get("nin")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"verified": False, "message": "Malformed JSON"},
                status=400,
            )
    else:
        nin = request.POST.get("nin")

    if not nin:
        return JsonResponse(
            {"verified": False, "message": "NIN is required"},
            status=400,
        )

    nin = nin.strip()

    # ----------------------------------
    # Validate NIN format
    # ----------------------------------
    if not re.fullmatch(r"\d{11}", nin):
        return JsonResponse(
            {"verified": False, "message": "Invalid NIN format"},
            status=400,
        )

    # ----------------------------------
    # STAGING MODE (MOCK SUCCESS)
    # ----------------------------------
    if settings.ENVIRONMENT == "staging":
        request.session["nin_verified"] = True
        request.session["verified_nin"] = nin

        return JsonResponse({
            "verified": True,
            "message": "NIN verified (staging mode)",
        })

    # ----------------------------------
    # PRODUCTION MODE (VerifyMe)
    # ----------------------------------
    try:
        response = requests.post(
            settings.VERIFYME_NIN_URL,
            headers={
                "Authorization": f"Bearer {settings.VERIFYME_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"nin": nin},
            timeout=15,
        )

        if response.status_code != 200:
            return JsonResponse(
                {
                    "verified": False,
                    "message": "Verification service unavailable",
                },
                status=503,
            )

        data = response.json()

        if data.get("status") is True:
            request.session["nin_verified"] = True
            request.session["verified_nin"] = nin

            return JsonResponse({
                "verified": True,
                "message": "NIN verified successfully",
            })

        return JsonResponse(
            {"verified": False, "message": "NIN verification failed"},
            status=400,
        )

    except requests.RequestException:
        return JsonResponse(
            {"verified": False, "message": "Verification service unavailable"},
            status=503,
        )


# =====================================================
# LOGIN
# =====================================================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(
                request,
                username=user_obj.username,
                password=password,
            )
        except User.DoesNotExist:
            user = None

        if user and user.is_active:
            login(request, user)
            messages.success(request, "Login successful.")

            try:
                if user.is_admin_user:
                    return redirect("/admin/")
                if user.is_lga_officer:
                    return redirect(reverse("lga:dashboard"))
                return redirect(reverse("applications:dashboard"))
            except NoReverseMatch:
                return redirect("/")

        messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")


# =====================================================
# DASHBOARD ROUTER
# =====================================================
@login_required
def dashboard_view(request):
    user = request.user

    if user.is_admin_user:
        return redirect("/admin/")
    if user.is_citizen:
        return redirect(reverse("applications:dashboard"))
    if user.is_lga_officer:
        return redirect(reverse("accounts:lga_assignment"))

    messages.error(request, "Unauthorized access.")
    return redirect("/")


# =====================================================
# LGA OFFICER — ASSIGNMENT
# =====================================================
@login_required
@lga_officer_required
def lga_assignment_view(request):
    form = LGAOfficerAssignmentForm(
        request.POST or None,
        instance=request.user,
        user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Local Government Area assignment updated successfully."
        )
        return redirect(reverse("lga:dashboard"))

    return render(
        request,
        "accounts/dashboard.html",
        {"lga_form": form},
    )


# =====================================================
# PROFILE
# =====================================================
@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


# =====================================================
# LOGOUT
# =====================================================
@login_required
def logout_custom(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("/")

# =====================================================
# idle session termination for all users
# =====================================================

@login_required
@require_POST
def keep_alive(request):
    request.session.modified = True
    return JsonResponse({"status": "alive"})