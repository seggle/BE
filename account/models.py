from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.TextField(max_length=20, primary_key=True, unique=True)
    name = models.TextField(null=True)
    email = models.TextField(null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    privilege = models.IntegerField(null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username']
    class Meta:
        db_table = "user"