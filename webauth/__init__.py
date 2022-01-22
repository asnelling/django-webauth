REDIRECT_FIELD_NAME = "next"


def user_is_webauth_verified(request) -> bool:
    """
    Checks if the user is logged in AND completed two factor authentication
    using Web Authentication.
    """
    if not request.user.is_authenticated:
        return False
    device_id = request.session.get("webauth_device_id", None)
    return request.user.webauth_devices.filter(id=device_id).exists()
