from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid


# =================================================
# CUSTOM USER MANAGER
# =================================================
class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        if not username:
            raise ValueError("Username is required")

        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create system administrator.
        """

        extra_fields["role"] = User.ROLE_ADMIN
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True

        if extra_fields.get("role") != User.ROLE_ADMIN:
            raise ValueError("Superuser must have role=ADMIN")

        return self.create_user(username, email, password, **extra_fields)


# =================================================
# CUSTOM USER MODEL
# =================================================
class User(AbstractUser):
    """
    Custom User model for LGAC Portal
    """

    nin = models.CharField(max_length=11, unique=True)
    nin_verified = models.BooleanField(default=False)

    # =================================================
    # ROLE DEFINITIONS
    # =================================================
    ROLE_CITIZEN = "CITIZEN"
    ROLE_LGA_OFFICER = "LGA_OFFICER"
    ROLE_ADMIN = "ADMIN"

    ROLE_CHOICES = (
        (ROLE_CITIZEN, "Citizen"),
        (ROLE_LGA_OFFICER, "LGA Officer"),
        (ROLE_ADMIN, "Administrator"),
    )

    # =================================================
    # CORE IDENTITY
    # =================================================
    full_name = models.CharField(
        max_length=150,
        help_text="Applicant full legal name",
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="Primary email address",
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="User phone number",
    )

    nin = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        help_text="National Identification Number (optional)",
    )

    # =================================================
    # ROLE & ACCESS CONTROL
    # =================================================
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CITIZEN,
        help_text="System role (admin-managed)",
    )

    lga = models.ForeignKey(
        "lgas.LGA",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="officers",
        help_text="Required when role is LGA Officer",
    )

    # =================================================
    # AUTH CONFIGURATION
    # =================================================
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone", "full_name"]

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
    )

    objects = UserManager()

    # =================================================
    # STRING
    # =================================================
    def __str__(self):
        return f"{self.full_name} ({self.email})"

    # =================================================
    # ROLE HELPERS
    # =================================================
    @property
    def is_citizen(self):
        return self.role == self.ROLE_CITIZEN

    @property
    def is_lga_officer(self):
        return self.role == self.ROLE_LGA_OFFICER

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN

    # =================================================
    # MODEL VALIDATION
    # =================================================
    def clean(self):
        if self.role == self.ROLE_LGA_OFFICER and not self.lga:
            raise ValidationError(
                {"lga": "LGA Officer must be assigned to a Local Government Area."}
            )

        if self.role != self.ROLE_LGA_OFFICER and self.lga:
            raise ValidationError(
                {"lga": "Only LGA Officers can be assigned to an LGA."}
            )

        if not self.username:
            base = slugify(self.full_name) or "user"
            self.username = f"{base}-{uuid.uuid4().hex[:6]}"

        super().clean()

    # =================================================
    # SAVE OVERRIDE (ROLE-AWARE, SAFE)
    # =================================================
    def save(self, *args, **kwargs):
        """
        Enforce role-based permissions without breaking admin UX.
        """

        # Always validate
        self.full_clean()

        if self.role == self.ROLE_ADMIN:
            self.is_staff = True
            self.is_superuser = True
            self.is_active = True

        elif self.role == self.ROLE_LGA_OFFICER:
            self.is_staff = True
            self.is_superuser = False
            self.is_active = True

        else:  # CITIZEN
            self.is_staff = False
            self.is_superuser = False
            self.is_active = True

        super().save(*args, **kwargs)
