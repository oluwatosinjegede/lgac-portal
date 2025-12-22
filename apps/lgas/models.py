from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class LGA(models.Model):
    """
    Local Government Area (LGA)

    Authoritative entity used for:
    • Citizen applications
    • Certificate generation
    • Branding (seal & signatures)
    • Administrative workflows
    """

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=10, unique=True)

    seal = models.ImageField(upload_to="lga_seals/")
    hlga_signature = models.ImageField(upload_to="lga_signatures/hlga/")
    chairman_signature = models.ImageField(upload_to="lga_signatures/chairman/")

    # =========================
    # CORE IDENTITY
    # =========================
    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Official name of the Local Government Area",
    )

    slug = models.SlugField(
        max_length=150,
        blank=True,
        db_index=True,
        help_text="Certificate-safe identifier (auto-generated, stable)",
    )

    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text="Official LGA short code (used in numbering and references)",
    )

    # =========================
    # STATUS / VISIBILITY
    # =========================
    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether this LGA is selectable by applicants",
    )

    # =========================
    # OFFICIAL BRANDING (CERTIFICATES)
    # =========================
    seal = models.ImageField(
        upload_to="lga/seals/",
        blank=True,
        null=True,
    )

    hlga_signature = models.ImageField(
        upload_to="lga/signatures/hlga/",
        blank=True,
        null=True,
    )

    chairman_signature = models.ImageField(
        upload_to="lga/signatures/chairman/",
        blank=True,
        null=True,
    )

    # =========================
    # AUDIT
    # =========================
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date this LGA was created in the system",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Local Government Area"
        verbose_name_plural = "Local Government Areas"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    # =========================
    # VALIDATION
    # =========================
    def clean(self):
        """
        Business-level validation.
        Does NOT block saving incomplete LGAs,
        but allows enforcement before certificate issuance.
        """
        if self.is_active:
            if not self.code:
                raise ValidationError({
                    "code": "Active LGAs must have an official code."
                })

    def validate_certificate_assets(self):
        """
        Hard validation to be called before certificate generation.
        """
        missing = []

        if not self.seal:
            missing.append("Official Seal")
        if not self.hlga_signature:
            missing.append("HLGA Signature")
        if not self.chairman_signature:
            missing.append("Chairman Signature")

        if missing:
            raise ValidationError(
                f"Cannot issue certificate for {self.name}. "
                f"Missing: {', '.join(missing)}"
            )
    
    def lga_asset_path(instance, filename, asset_type):
        """
        Stores files as:
        lga_assets/<LGA_CODE>/<asset_type>.png
        """
        if not instance.code:
            raise ValueError("LGA code must be set before uploading assets")

        ext = filename.split(".")[-1]
        return f"lga_assets/{instance.code.upper()}/{asset_type}.{ext}"


    # =========================
    # LIFECYCLE
    # =========================
    def save(self, *args, **kwargs):
        """
        Auto-generate slug if missing.
        Slug is intentionally NOT unique to avoid legacy migration conflicts.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # =========================
    # REPRESENTATION
    # =========================
    def __str__(self):
        return self.name
