from django.db import models
from django.conf import settings
from django.urls import reverse


class WebAuthnCredential(models.Model):
    name = models.CharField(max_length=250)
    rp_id = models.CharField(max_length=250)
    origin = models.CharField(max_length=250)
    raw_id = models.CharField(max_length=300, unique=True)
    credential_id = models.CharField(max_length=250)
    public_key = models.TextField()
    sign_count = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )


    def get_absolute_url(self):
        return reverse("key-detail", kwargs={"pk": self.pk})
    
