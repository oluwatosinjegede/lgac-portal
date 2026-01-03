from django import forms
from .models import Application
from apps.lgas.models import LGA


class ApplicationForm(forms.ModelForm):
    """
    LGAC Application Form

    • Identity fields are READ-ONLY
    • Identity values are populated from logged-in user
    • Identity snapshot is persisted on save
    """

    # =========================
    # READ-ONLY DISPLAY FIELDS
    # =========================
    full_name = forms.CharField(
        required=False,
        disabled=True,
        label="Full Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    email = forms.EmailField(
        required=False,
        disabled=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    phone = forms.CharField(
        required=False,
        disabled=True,
        label="Telephone Number",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    nin = forms.CharField(
        required=False,
        disabled=True,
        label="National Identification Number (NIN)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # =========================
    # META
    # =========================
    class Meta:
        model = Application
        fields = [
            "lga",                 # ✅ REQUIRED (FIX)
            "full_name",
            "date_of_birth",
            "place_of_birth",
            "nin",
            "phone",
            "email",
            "home_town",
            "family_compound",
            "father_name",
            "mother_name",
            "purpose",
            "passport_photo",
        ]

        widgets = {
            "lga": forms.Select(attrs={"class": "form-select"}),
            "home_town": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Oke-Aro",
            }),
            "family_compound": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Ajana Compound",
            }),
            "father_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Father’s full name",
            }),
            "mother_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Mother’s full name",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "purpose": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "State the purpose of this certificate",
            }),
            "passport_photo": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }

    # =========================
    # INITIALIZATION
    # =========================
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Show ONLY active LGAs
        self.fields["lga"].queryset = LGA.objects.filter(is_active=True)

        # Populate read-only identity fields
        if user:
            self.user = user
            self.fields["full_name"].initial = user.full_name
            self.fields["email"].initial = user.email
            self.fields["phone"].initial = user.phone
            self.fields["nin"].initial = user.nin

    # =========================
    # FIELD VALIDATION
    # =========================
    def clean_passport_photo(self):
        photo = self.cleaned_data.get("passport_photo")
        if not photo:
            raise forms.ValidationError("Passport photograph is required.")
        if photo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Passport photo must not exceed 2MB.")
        return photo

    # =========================
    # SAVE OVERRIDE (CRITICAL)
    # =========================
    def save(self, commit=True):
        """
        Persist identity snapshot into Application model
        """
        instance = super().save(commit=False)

        if hasattr(self, "user"):
            instance.full_name = self.user.full_name
            instance.email = self.user.email
            instance.phone = self.user.phone
            instance.nin = self.user.nin

        if commit:
            instance.save()

        return instance
