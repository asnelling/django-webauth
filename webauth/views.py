import base64
import binascii
import json
import secrets
import time


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.views import View
from django.template.response import TemplateResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy

import webauthn

from . import REDIRECT_FIELD_NAME
from .forms import KeyCreateForm, KeyAuthenticateForm
from .models import WebAuthnCredential


# EdDSA
COSE_EDDSA = -8

# ECDSA w/ SHA-256
COSE_ES256 = -7

# ECDSA w/ SHA-384
COSE_ES384 = -35

# ECDSA w/ SHA-512
COSE_ES512 = -36

# RSASSA-PSS w/ SHA-256
COSE_PS256 = -37

# RSASSA-PSS w/ SHA-384
COSE_PS384 = -38

# RSASSA-PSS w/ SHA-512
COSE_PS512 = -39

# RSASSA-PKCS1-v1_5 using SHA-256
COSE_RS256 = -257

# RSASSA-PKCS1-v1_5 using SHA-384
COSE_RS384 = -258

# RSASSA-PKCS1-v1_5 using SHA-512
COSE_RS512 = -259


class UserFilterMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class KeyList(UserFilterMixin, LoginRequiredMixin, ListView):
    model = WebAuthnCredential


class KeyDetail(UserFilterMixin, LoginRequiredMixin, DetailView):
    model = WebAuthnCredential


class KeyDelete(UserFilterMixin, LoginRequiredMixin, DeleteView):
    model = WebAuthnCredential
    success_url = reverse_lazy("key-list")


class KeyCreate(UserFilterMixin, LoginRequiredMixin, FormView):
    template_name = "webauth/webauthncredential_create.html"
    form_class = KeyCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "challenge": self.request.session.get("webauthn_challenge"),
                "user": self.request.user,
            }
        )
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        if self.request.method == "GET":
            challenge = secrets.token_urlsafe(settings.WEBAUTHN_CHALLENGE_NBYTES)
            self.request.session["webauthn_challenge"] = challenge

            user = self.request.user
            options = {
                "challenge": challenge,
                "rp": {
                    "id": settings.WEBAUTHN_RP_ID,
                    "name": settings.WEBAUTHN_RP_NAME,
                    "icon": settings.WEBAUTHN_RP_ICON,
                },
                "user": {
                    "id": user.username,
                    "name": user.username,
                    "displayName": user.get_full_name(),
                },
                "pubKeyCredParams": [
                    {
                        "type": "public-key",
                        "alg": COSE_ES256,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_ES384,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_ES512,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_RS256,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_RS384,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_RS512,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_PS256,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_PS384,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_PS512,
                    },
                    {
                        "type": "public-key",
                        "alg": COSE_EDDSA,
                    },
                ],
                "attestation": "direct",
                "authenticator_selection": {
                    "userVerification": settings.WEBAUTHN_USER_VERIFICATION,
                },
                "timeout": settings.WEBAUTHN_CREATE_TIMEOUT,
            }
            kwargs["options"] = json.dumps(options)
        return super().get_context_data(**kwargs)


class KeyAuthenticate(LoginRequiredMixin, FormView):
    template_name = "webauth/authenticate.html"
    form_class = KeyAuthenticateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request,
        })
        return kwargs
    

    def get_context_data(self, **kwargs):
        challenge = secrets.token_urlsafe(settings.WEBAUTHN_CHALLENGE_NBYTES)
        self.request.session["webauthn_challenge"] = challenge

        credential_ids = WebAuthnCredential.objects.filter(
            user=self.request.user
        ).values_list("raw_id", flat=True)

        options = {
            "challenge": challenge,
            "allowCredentials": [
                {"id": i, "type": "public-key"} for i in credential_ids
            ],
            "rpId": settings.WEBAUTHN_RP_ID,
            "timeout": settings.WEBAUTHN_GET_TIMEOUT,
            "userVerification": settings.WEBAUTHN_USER_VERIFICATION,
        }
        kwargs['options'] = json.dumps(options)

        return super().get_context_data(**kwargs)
    

    def get_success_url(self):
        return settings.LOGIN_REDIRECT_URL
