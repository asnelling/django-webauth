import time

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

import webauthn

from .models import WebAuthnCredential


class KeyCreateForm(forms.Form):
    name = forms.CharField(max_length=250)
    raw_id = forms.CharField(widget=forms.HiddenInput())
    client_data = forms.CharField(widget=forms.HiddenInput())
    att_obj = forms.CharField(widget=forms.HiddenInput())
    type = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, challenge: str = None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.challenge = challenge
        self.instance = None
        self.user = user


    def clean(self):
        cleaned_data = super().clean()
        cred = {
            'rawId': cleaned_data.get("raw_id"),
            'clientData': cleaned_data.get("client_data"),
            'attObj': cleaned_data.get("att_obj"),
            'type': cleaned_data.get('type'),
        }
        webauthn_registration_response = webauthn.WebAuthnRegistrationResponse(
            settings.WEBAUTHN_RP_ID,
            settings.WEBAUTHN_ORIGIN,
            cred,
            self.challenge,
        )

        try:
            wc = webauthn_registration_response.verify()
        except Exception as e:
            raise ValidationError("Credential verification failed") from e
        else:
            self.instance = WebAuthnCredential(
                name=cleaned_data.get("name"),
                rp_id=wc.rp_id,
                origin=wc.origin,
                credential_id=str(wc.credential_id, encoding="utf-8"),
                raw_id=cred.get("rawId"),
                public_key=str(wc.public_key, encoding="utf-8"),
                sign_count=wc.sign_count,
                user=self.user,
            )
        
        return cleaned_data
    

    def save(self):
        self.instance.save()
        return self.instance


class KeyAuthenticateForm(forms.Form):
    assertion_response = forms.JSONField()


    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    

    def clean(self):
        cleaned_data = super().clean()
        user = authenticate(self.request, publicKey=cleaned_data.get('assertion_response'))
        if user is None:
            raise ValidationError("Assertion verification failed")
        
        self.request.session['webauthn_authenticated_at'] = int(time.time()*1000)

        return cleaned_data
