import uuid

from django.db import models

from usersproj import settings


class ExpiredToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jti


class RefreshToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token_family = models.CharField(max_length=255, default=uuid.uuid4)
    is_revoked = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def revoke_family(self):
        RefreshToken.objects.filter(token_family=self.token_family).update(is_revoked=True)
