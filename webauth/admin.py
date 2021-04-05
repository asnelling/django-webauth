from django.contrib import admin

from .models import WebAuthnCredential


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    list_display = ('raw_id', 'sign_count')
    fields = ('rp_id', 'origin', 'raw_id', 'credential_id', 'public_key', 'sign_count', 'user')
    readonly_fields = ('credential_id', 'public_key')
