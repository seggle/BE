from django.db import models

from account.models import User

# Create your models here.
class Announcement(models.Model):
    title = models.TextField()
    context = models.TextField()
    created_user = models.Foreignkey(User, on_delete=models.CASCADE, db_name="created_user")
    created_time = models.DateTimeField()
    last_modified = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)
    important = models.BooleanField(default=False)

    class Meta:
        db_table = "announcement"