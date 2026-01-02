from django.db import models

class LGA(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Official LGA code (optional)",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Local Government Area"
        verbose_name_plural = "Local Government Areas"

    def __str__(self):
        return self.name
