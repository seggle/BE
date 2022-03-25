from django.db import models

from account.models import User

# Create your models here.
class Proposal(models.Model):
    title = models.TextField()
    context = models.TextField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user", to_field="username")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "proposal"