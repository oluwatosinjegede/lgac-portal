from django.contrib import admin, messages
from django.utils.html import format_html

from .models import LGA


@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    # =========================
    # LIST VIEW
    # =========================
    list_display = (
        "id",
        "name",
        "code",
        "is_active",
        "certificate_ready",
        "created_at",
    )

    list_filter = ("is_active",)
    search_fields = ("name", "code", "slug")
    ordering = ("name",)

    # =========================
    # FORM LAYOUT (SAFE)
    # =========================
    fieldsets = (
        ("Core Identity", {
            "fields": ("name", "slug", "code", "is_active"),
        }),
        ("Certificate Branding (Required for Issuance)", {
            "fields": (
                "seal",
                "seal_preview",
                "hlga_signature",
                "chairman_signature",
            ),
            "description": (
                "These assets are mandatory before certificates can be issued "
                "for this Local Government."
            ),
        }),
    )

    # =========================
    # READ-ONLY / AUDIT FIELDS
    # =========================
    readonly_fields = (
        "seal_preview",
        "created_at",
    )

    # ⚠️ CRITICAL: non-editable fields must be excluded
    exclude = ("created_at",)

    # =========================
    # BULK ACTIONS
    # =========================
    actions = ("activate_lgas", "deactivate_lgas")

    # =========================
    # COMPUTED COLUMNS
    # =========================
    @admin.display(boolean=True, description="Certificate Ready")
    def certificate_ready(self, obj: LGA) -> bool:
        return bool(
            obj.is_active
            and obj.code
            and obj.seal
            and obj.hlga_signature
            and obj.chairman_signature
        )

    # =========================
    # ACTIONS
    # =========================
    def activate_lgas(self, request, queryset):
        activated = 0
        blocked = []

        for lga in queryset:
            if not lga.code:
                blocked.append(lga.name)
                continue

            lga.is_active = True
            lga.save(update_fields=["is_active"])
            activated += 1

        if activated:
            self.message_user(
                request,
                f"{activated} Local Government(s) activated.",
                level=messages.SUCCESS,
            )

        if blocked:
            self.message_user(
                request,
                (
                    "The following LGAs were NOT activated because they lack "
                    f"an official code: {', '.join(blocked)}"
                ),
                level=messages.WARNING,
            )

    activate_lgas.short_description = "Activate selected LGAs"

    def deactivate_lgas(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(
            request,
            "Selected Local Governments deactivated.",
            level=messages.INFO,
        )

    deactivate_lgas.short_description = "Deactivate selected LGAs"

    # =========================
    # PREVIEW HELPERS
    # =========================
    def seal_preview(self, obj):
        if obj.seal:
            return format_html('<img src="{}" width="120"/>', obj.seal.url)
        return "—"
