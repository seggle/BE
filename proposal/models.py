from django.db import models

from account.models import User

# Create your models here.
class Proposal(models.Model):
    title = models.TextField()
    # context = RichTextField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_name="created_user")
    created_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "proposal"