=======
WebAuth
=======

Two Factor Authentication in Django using Web Authentication API (WebAuthn).

Quick start
-----------

1. Add "webauth" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'webauth',
    ]

2. Include the webauth URLconf in your project urls.py like this::

    path('webauth/', include('webauth.urls')),

3. Add ``webauth.backends.WebAuthnBackend`` to ``AUTHENTICATION_BACKENDS`` setting::
   
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'webauth.backends.WebAuthnBackend',
    ]

4. Add ``webauth.mixins.WebAuthnRequiredMixin`` to any views you want to
   protect with WebAuthn::

    from webauth.mixins import WebAuthnRequiredMixin

    class AuthorList(WebAuthnRequiredMixin, ListView):
        ...
    
   Only class-based views are currently supported.

5. Run ``python manage.py migrate`` to create the webauth models.

6. Start the development server and visit http://127.0.0.1:8000/webauth/keys/
   to register a WebAuthn credential.

7. Visit http://127.0.0.1:8000/webauth/auth/ to test your new authenticator.

When visiting views marked with ``WebAuthnRequiredMixin``, you will have to
authenticate using a credential you created in step 6 if not already done so
for the current session. Traditional authentication (username and password)
is also required. The ``WebAuthnRequiredMixin`` will use redirects to complete
any required authentication.
