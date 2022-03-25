from django.db import models

from account.models import User

# Create your models here.
class Announcement(models.Model):
    title = models.TextField()
    context = models.TextField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user", to_field="username")
    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)
    important = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "announcement"