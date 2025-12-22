from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.lgas.models import LGA


class Application(models.Model):

    # =========================
    # STATUS CONSTANTS
    # =========================
    STATUS_DRAFT = "DRAFT"
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_PAID = "PAID"
    STATUS_IN_REVIEW = "IN_REVIEW"
    STATUS_APPROVED = "APPROVED"
    STATUS_WITHDRAWN = "WITHDRAWN"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_PAID, "Paid"),
        (STATUS_IN_REVIEW, "In Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_WITHDRAWN, "Withdrawn"),
    ]

    # =========================
    # OWNERSHIP
    # =========================
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    lga = models.ForeignKey(
        LGA,
        on_delete=models.PROTECT,
        related_name="applications",
    )

    # =========================
    # IDENTITY SNAPSHOT (IMMUTABLE)
    # =========================
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    nin = models.CharField(max_length=20)

    # =========================
    # PERSONAL DETAILS
    # =========================
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(
        max_length=100,
        default="Not Provided",
    )

    home_town = models.CharField(max_length=100)
    family_compound = models.CharField(max_length=150)
    father_name = models.CharField(max_length=150)
    mother_name = models.CharField(max_length=150)

    purpose = models.TextField()

    # =========================
    # PASSPORT PHOTO (MIGRATION-SAFE)
    # =========================
    passport_photo = models.ImageField(
        upload_to="passports/",
        null=True,        # legacy-safe
        blank=False
    )

    # =========================
    # WORKFLOW
    # =========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================
    # CERTIFICATE METADATA (NEW)
    # =========================
    certificate_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    certificate_hash = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # =========================
    # MODEL GUARANTEES
    # =========================
    def clean(self):
        """
        Hard validation – safe during form validation and saves
        """

        # SAFE FK CHECK
        if not self.lga_id:
            raise ValidationError({
                "lga": "Local Government selection is required."
            })

        # Identity snapshot must exist once submitted
        if self.status != self.STATUS_DRAFT:
            missing = []

            if not self.full_name:
                missing.append("Full name")
            if not self.email:
                missing.append("Email")
            if not self.phone:
                missing.append("Phone number")
            if not self.nin:
                missing.append("NIN")

            if missing:
                raise ValidationError(
                    f"Identity snapshot incomplete: {', '.join(missing)}"
                )

            if not self.passport_photo:
                raise ValidationError({
                    "passport_photo": "Passport photograph is required before submission."
                })

    # =========================
    # DOMAIN METHODS
    # =========================
    def snapshot_identity_from_user(self):
        """
        Capture immutable identity snapshot from applicant
        """
        user = self.applicant
        self.full_name = user.full_name
        self.email = user.email
        self.phone = user.phone
        self.nin = user.nin

    def submit(self):
        """
        Single, authoritative submission action
        """
        self.snapshot_identity_from_user()
        self.status = self.STATUS_SUBMITTED
        self.full_clean()
        self.save(update_fields=[
            "full_name",
            "email",
            "phone",
            "nin",
            "status",
        ])

    # Application model
    #ertificate_seal = models.ImageField(upload_to="certificates/seals/", null=True)
    #ertificate_hlga_signature = models.ImageField(upload_to="certificates/hlga/", null=True)
    #ertificate_chairman_signature = models.ImageField(upload_to="certificates/chairman/", null=True)


    def __str__(self):
        return f"{self.full_name} – {self.lga.name}"
