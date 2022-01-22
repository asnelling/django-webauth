# django-webauth

Multi-Factor Authentication (MFA, 2FA) for Django using the
[Web Authentication API][api].

![django-webauth demo](https://raw.githubusercontent.com/asnelling/django-webauth/master/demo.gif)

## Quick Start

1. Install `django-webauth` using pip

    ```Shell
    $ pip install django-webauth
    ```

2. Add `webauth` to INSTALLED_APPS

    ```Python
    # settings.py
    INSTALLED_APPS = [
        ...
        "webauth",
    ]
    ```

3. Add django-webauth URLs

    ```Python
    # urls.py
    urlpatterns = [
        ...
        path("webauth/", include("webauth.urls")),
    ]
    ```

4. Add Web Authentication protection to your views. How you do this depends on
   whether you're protecting function views or class based views:

    1.  **To protect view functions:**

        Add the `@webauth_required` decorator to disallow users that have not
        authenticated with webauth.

        ```Python
        # views.py
        from webauth.decorators import webauth_required

        @webauth_required
        def private_view(request):
            ...
        ```

    2.  **To protect class based views:**

        Add `WebAuthRequiredMixin` to the inheritance list on your view classes.

        ```Python
        # views.py
        from webauth.mixins import WebAuthRequiredMixin

        class YourClassBasedView(WebAuthRequiredMixin, View):
            ...
        ```

5. Set some required `django-webauth` settings

    ```Python
    # settings.py
    WEBAUTH_RP_ID = "localhost"
    WEBAUTH_RP_NAME = "Example Site"
    WEBAUTH_ORIGIN = "http://localhost:8000"
    WEBAUTH_VERIFY_URL = "/webauth/verify/"
    ```

6. Run migrations to create the table for storing authenticator data

    ```Shell
    $ python manage.py migrate
    ```

7. Run your Django app and register a new security key at
   http://localhost:8000/webauth/register/

8. Navigate to a view you protected in step 4. `django-webauth` will redirect
   you to a page that will attempt to authenticate using your newly created
   key. If successful, you will be redirected to the protected view.


## Customizing the built-in templates

`django-webauth` includes templates out of the box to get you up and running.
The templates extend `webauth/base.html`, which you will likely want to replace
with your own base template.

Replace the built-in base template simply by creating a new `webauth/base.html`
in your app's `templates` folder. See [How to override templates][templates]
from the Django documentation for more info.

You are also welcome, and encouraged, to replace the other included templates
with your own using the same method.

## Configuration settings

[`WEBAUTH_RP_ID`][rp_id]: the hostname (minus scheme and port) of the server running
your Django app

[`WEBAUTH_RP_NAME`][rp_name]: human readable name of your server intended only
for display

[`WEBAUTH_ORIGIN`][origin]: used for verifying assertions. Only authentication
ceremonies occurring in this origin will validate

`WEBAUTH_VERIFY_URL`: Users not authenticated with `django-webauth` will
redirect users here when they request a protected view. This "login" page
completes the multi-factor authentication flow.

[api]: https://w3c.github.io/webauthn/
[templates]: https://docs.djangoproject.com/en/4.0/howto/overriding-templates/
[rp_id]: https://w3c.github.io/webauthn/#rp-id
[rp_name]: https://w3c.github.io/webauthn/#dom-publickeycredentialentity-name
[origin]: https://w3c.github.io/webauthn/#dom-collectedclientdata-origin
