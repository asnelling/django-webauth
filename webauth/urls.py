from django.urls import path

from . import views


app_name = "webauth"
urlpatterns = [
    path("devices/", views.DeviceListView.as_view(), name="devices"),
    path("devices/<int:pk>/delete/", views.DeleteDevice.as_view(), name="delete"),
    path("registration/", views.Registration.as_view(), name="registration"),
    path("verify/", views.verify, name="verify"),
    path("verification/", views.Verification.as_view(), name="verification"),
]
