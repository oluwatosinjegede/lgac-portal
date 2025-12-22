from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User
from apps.lgas.models import LGA

import uuid
import re


# ======================================================
# PUBLIC SIGNUP FORM (CITIZEN ONLY)
# ======================================================
class SignupForm(UserCreationForm):
    """
    Public signup form (Citizen only).
    NIN is mandatory and MUST be verified before submission.
    Verification state is enforced server-side via session.
    """

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Oluwatosin Paul Jegede",
            "autocomplete": "name",
        }),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )

    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 08012345678 or +2348012345678",
            "autocomplete": "tel",
        }),
    )

    nin = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "11-digit NIN",
            "id": "id_nin",  # REQUIRED for JS verification
        }),
    )

    class Meta:
        model = User
        fields = (
            "full_name",
            "email",
            "phone",
            "nin",
            "password1",
            "password2",
        )

    # ==================================================
    # FIELD-LEVEL VALIDATION
    # ==================================================
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip().replace(" ", "")
        if not re.fullmatch(r"\+?\d{10,15}", phone):
            raise ValidationError("Enter a valid phone number.")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("An account with this phone number already exists.")
        return phone

    def clean_nin(self):
        nin = self.cleaned_data.get("nin", "").strip()
        if not nin.isdigit() or len(nin) != 11:
            raise ValidationError("NIN must be exactly 11 digits.")
        return nin

    # ==================================================
    # FORM-LEVEL VALIDATION (NIN VERIFICATION ENFORCEMENT)
    # ==================================================
    def clean(self):
        cleaned_data = super().clean()

        request = self.initial.get("request")
        if not request:
            raise ValidationError("Session error. Please refresh and try again.")

        if not request.session.get("nin_verified"):
            raise ValidationError("You must verify your NIN before submitting this form.")

        verified_nin = request.session.get("verified_nin")
        entered_nin = cleaned_data.get("nin")

        if verified_nin != entered_nin:
            raise ValidationError(
                "The verified NIN does not match the entered NIN. Please re-verify."
            )

        return cleaned_data

    # ==================================================
    # SAVE
    # ==================================================
    def save(self, commit=True):
        user = super().save(commit=False)

        # System-generated, non-guessable username
        user.username = f"user_{uuid.uuid4().hex[:10]}"

        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.nin = self.cleaned_data["nin"]

        # Public signup = Citizen only
        user.role = User.ROLE_CITIZEN
        user.is_active = True

        if commit:
            user.save()

        return user


# ======================================================
# LGA OFFICER ASSIGNMENT FORM (DASHBOARD USE)
# ======================================================
class LGAOfficerAssignmentForm(forms.ModelForm):
    """
    Allows LGA Officers to select an active LGA.
    Must be instantiated with `user=request.user`.
    """

    class Meta:
        model = User
        fields = ("lga",)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Restrict to active LGAs only
        self.fields["lga"].queryset = LGA.objects.filter(is_active=True)

        # Only LGA officers may interact
        if not user or user.role != User.ROLE_LGA_OFFICER:
            self.fields["lga"].disabled = True
