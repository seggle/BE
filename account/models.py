from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.TextField(max_length=20, unique=True)
    name = models.TextField(null=True)
    email = models.TextField(null=True)
    privilege = models.IntegerField(null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    class Meta:
        db_table = "user"

class ResetPassword(models.Model):
    email = models.CharField(max_length=200, null=True)
    token = models.CharField(max_length=255, null=True)
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return self.token
    # This thing creates users personalized link, that they visit and have a enter new password view in Front-End.
    def get_absolute_url(self):
        return f'/{self.token}/'