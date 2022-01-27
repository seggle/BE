from django.db import models
from account.models import User

# Create your models here.
class Faq(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user")
    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "faq"