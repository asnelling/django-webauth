from http import HTTPStatus
import json
from secrets import token_hex

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from webauthn import verify_authentication_response, verify_registration_response
from webauthn.helpers.structs import AuthenticationCredential, RegistrationCredential

from .models import WebAuthDevice


class DeviceListView(ListView, LoginRequiredMixin):
    model = WebAuthDevice

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class DeleteDevice(DeleteView):
    model = WebAuthDevice
    success_url = reverse_lazy("webauth:devices")

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class Registration(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        display_name = request.user.get_full_name() or request.user.username
        challenge = token_hex()
        request.session["webauth_challenge"] = challenge

        hex_id = f"{request.user.id:x}"
        if len(hex_id) % 2 == 1:
            hex_id = f"0{hex_id}"

        return JsonResponse(
            {
                "publicKey": {
                    "rp": {
                        "id": settings.WEBAUTH_RP_ID,
                        "name": settings.WEBAUTH_RP_NAME,
                    },
                    "user": {
                        "id": hex_id,
                        "name": request.user.email,
                        "displayName": display_name,
                    },
                    "pubKeyCredParams": [
                        {
                            "type": "public-key",
                            "alg": -7,
                        },
                    ],
                    "attestation": "direct",
                    "timeout": 60000,
                    "challenge": challenge,
                },
            }
        )

    def post(self, request, *args, **kwargs):
        challenge = bytes.fromhex(request.session.pop("webauth_challenge"))

        data = json.loads(request.body)
        name = data.get("name")
        pub_key_credential = json.dumps(data.get("pubKeyCredential"))

        verification = verify_registration_response(
            credential=RegistrationCredential.parse_raw(pub_key_credential),
            expected_challenge=challenge,
            expected_origin=settings.WEBAUTH_ORIGIN,
            expected_rp_id=settings.WEBAUTH_RP_ID,
            require_user_verification=False,
        )
        WebAuthDevice.objects.create(
            user=request.user,
            name=name,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            format=verification.fmt,
            type=verification.credential_type,
            sign_count=verification.sign_count,
        )
        return HttpResponse(status=HTTPStatus.CREATED)


@login_required
def verify(request):
    return render(request, "webauth/webauthdevice_verify.html")


class Verification(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        challenge = token_hex()
        request.session["webauth_challenge"] = challenge

        credential_ids = WebAuthDevice.objects.filter(user=request.user).values_list(
            "credential_id", flat=True
        )

        return JsonResponse(
            {
                "publicKey": {
                    "challenge": challenge,
                    "allowCredentials": [
                        {
                            "id": credential_id.hex(),
                            "type": "public-key",
                            "transports": [
                                "usb",
                                "ble",
                                "nfc",
                            ],
                        }
                        for credential_id in credential_ids
                    ],
                    "timeout": 60000,
                },
            }
        )

    def post(self, request, *args, **kwargs):
        challenge = bytes.fromhex(request.session.pop("webauth_challenge"))

        credential = AuthenticationCredential.parse_raw(request.body.decode())
        device = WebAuthDevice.objects.get(credential_id=credential.raw_id)

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=settings.WEBAUTH_RP_ID,
            expected_origin=settings.WEBAUTH_ORIGIN,
            credential_public_key=device.public_key,
            credential_current_sign_count=device.sign_count,
            require_user_verification=False,
        )

        device.sign_count = verification.new_sign_count
        device.save()

        request.session["webauth_device_id"] = device.id

        return HttpResponse()
