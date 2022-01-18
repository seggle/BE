from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.TextField(max_length=20, primary_key=True, unique=True)
    name = models.TextField()
    email = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    privilege = models.IntegerField()

    class Meta:
        db_table = "user"