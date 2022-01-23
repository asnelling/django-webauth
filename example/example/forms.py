from functools import partial

from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.forms import ModelForm
from django.forms.utils import ErrorList


# StyledErrorList = partial(ErrorList, error_class="invalid-feedback")
class StyledErrorList(ErrorList):
    def __init__(self, *args, **kwargs):
        error_class = "invalid-feedback"
        if kwargs.get("error_class") == "nonfield":
            error_class = "text-danger"
        kwargs["error_class"] = error_class
        super().__init__(*args, **kwargs)


class StyledFormMixin:
    error_css_class = "is-invalid"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, error_class=StyledErrorList, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = field.css_classes("form-control")


class StyledModelForm(StyledFormMixin, ModelForm):
    pass


class StyledAuthenticationForm(StyledFormMixin, AuthenticationForm):
    pass


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    pass


class StyledUserCreationForm(StyledFormMixin, UserCreationForm):
    pass
