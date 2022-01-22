from django.contrib.auth.mixins import AccessMixin
from django.conf import settings

from . import user_is_webauth_verified


class WebAuthRequiredMixin(AccessMixin):
    """Verify the user passed BOTH authentication factors (password and Web
    Authentication)."""
    login_url = settings.WEBAUTH_VERIFY_URL

    def dispatch(self, request, *args, **kwargs):
        if not user_is_webauth_verified(request):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
