from urllib import parse

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import QueryDict, HttpResponseRedirect

from . import REDIRECT_FIELD_NAME


def redirect_to_webauthn(next, webauthn_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Redirect the user to the WebAuthn 2FA page, passing the given `next` page.
    """
    webauthn_url_parts = list(parse.urlparse(webauthn_url or settings.WEBAUTHN_URL))
    if redirect_field_name:
        querystring = QueryDict(webauthn_url_parts[4], mutable=True)
        querystring[redirect_field_name] = next
        webauthn_url_parts[4] = querystring.urlencode(safe='/')
    
    return HttpResponseRedirect(parse.urlunparse(webauthn_url_parts))


class WebAuthnRequiredMixin:
    """Verify that the current user is authenticated and passed 2FA with WebAuthn"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        elif not request.session.get('webauthn_authenticated_at'):
            return redirect_to_webauthn(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)
