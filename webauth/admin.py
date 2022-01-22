from django.contrib import admin

from .models import WebAuthDevice


@admin.register(WebAuthDevice)
class WebAuthDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
        "format",
        "type",
        "sign_count",
    )
