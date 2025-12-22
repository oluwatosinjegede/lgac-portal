from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


# ==================================================
# ADMIN FORM (ROLE-AWARE VALIDATION)
# ==================================================
class UserAdminForm(ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        lga = cleaned.get("lga")

        if role == User.ROLE_LGA_OFFICER and not lga:
            raise ValidationError({
                "lga": "LGA assignment is required when role is LGA Officer."
            })

        if role != User.ROLE_LGA_OFFICER and lga:
            raise ValidationError({
                "lga": "Only LGA Officers can be assigned an LGA."
            })

        return cleaned


# ==================================================
# USER ADMIN
# ==================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    form = UserAdminForm

    # ==================================================
    # LIST VIEW
    # ==================================================
    list_display = (
        "id",
        "full_name",
        "email",
        "username",
        "phone",
        "role",
        "lga",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = (
        "role",
        "lga",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "full_name",
        "email",
        "username",
        "phone",
        "nin",
    )

    ordering = ("-date_joined",)

    # ==================================================
    # EDIT USER VIEW (UX FIX IS HERE)
    # ==================================================
    fieldsets = (
        (_("Account Information"), {
            "fields": ("email", "username", "password"),
        }),
        (_("Personal Details"), {
            "fields": ("full_name", "phone", "nin"),
        }),
        (_("Role & Assignment"), {
            "fields": ("role", "lga"),
            "description": (
                "⚠️ If role is set to LGA Officer, an LGA MUST be assigned."
            ),
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        (_("Important Dates"), {
            "fields": ("last_login", "date_joined"),
        }),
    )

    # ==================================================
    # ADD USER (ADMIN ONLY)
    # ==================================================
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "full_name",
                    "email",
                    "phone",
                    "role",
                    "lga",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )

    # ==================================================
    # READ-ONLY FIELDS
    # ==================================================
    readonly_fields = (
        "username",
        "date_joined",
        "last_login",
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    # ==================================================
    # ADMIN SAFETY
    # ==================================================
    def get_readonly_fields(self, request, obj=None):
        """
        Username is system-generated and immutable.
        """
        if obj:
            return self.readonly_fields
        return ()
