# apps/payments/models.py

from django.db import models
from django.utils import timezone


class Payment(models.Model):

    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    )

    application = models.OneToOneField(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="payment",
    )

    reference = models.CharField(max_length=100, unique=True)
    amount = models.PositiveIntegerField()  # kobo
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    gateway_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_success(self):
        self.status = self.STATUS_SUCCESS
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

    def __str__(self):
        return f"{self.reference} ({self.status})"
