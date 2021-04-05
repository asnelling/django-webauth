from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import PermissionDenied
from webauthn import WebAuthnUser, WebAuthnAssertionResponse

from .models import WebAuthnCredential


class WebAuthnBackend(BaseBackend):
    def authenticate(self, request, publicKey=None):
        raw_id = publicKey.get('rawId')

        stored_credential = WebAuthnCredential.objects.filter(
            raw_id=raw_id,
        ).first()
        if not stored_credential:
            return None
        
        user = stored_credential.user
        wu = WebAuthnUser(
            user_id=user.username,
            username=user.username,
            display_name=user.get_full_name(),
            credential_id=stored_credential.credential_id,
            public_key=stored_credential.public_key,
            sign_count=stored_credential.sign_count,
            rp_id=stored_credential.rp_id,
            icon_url=None,
        )

        war = WebAuthnAssertionResponse(
            wu,
            publicKey,
            request.session.get('webauthn_challenge'),
            settings.WEBAUTHN_ORIGIN,
        )

        try:
            stored_credential.sign_count = war.verify()
            stored_credential.save()
        except Exception as e:
            raise PermissionDenied("Assertion verification failed.") from e
        
        return user
    

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
