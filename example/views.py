from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelform_factory
from django.shortcuts import render
from django.views.generic.edit import UpdateView, CreateView
from webauth.decorators import webauth_required

from .forms import StyledModelForm, StyledUserCreationForm


def home(request):
    return render(request, "home.html")


@webauth_required
def private(request):
    return render(request, "private.html")


class ProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = "profile.html"
    form_class = modelform_factory(
        get_user_model(),
        form=StyledModelForm,
        fields=["first_name", "last_name", "email"],
    )
    success_url = "/profile/"

    def get_object(self, queryset=None):
        return self.request.user


class RegisterView(CreateView):
    model = get_user_model()
    form_class = StyledUserCreationForm
    success_url = "/profile/"
    template_name = "example/register.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
