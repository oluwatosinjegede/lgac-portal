from django.contrib import admin
from .models import LGA

@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)

    actions = ["activate_lgas", "deactivate_lgas"]

    def activate_lgas(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected LGAs activated.")

    def deactivate_lgas(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected LGAs deactivated.")
