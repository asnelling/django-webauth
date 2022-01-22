from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.shortcuts import resolve_url

from . import REDIRECT_FIELD_NAME, user_is_webauth_verified


def webauth_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, verify_url=None
):
    """
    Decorator for views that ensures the user is logged in AND completed two
    factor authentication using Web Authentication. Redirects to the web
    authentication page otherwise.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if user_is_webauth_verified(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(verify_url or settings.WEBAUTH_VERIFY_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator
