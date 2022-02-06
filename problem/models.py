from django.db import models
#from contest.models import Contest
from account.models import User
from file.models import File

class Problem(models.Model):
    title = models.TextField()
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user")
    data = models.ForeignKey(File, on_delete=models.CASCADE, db_column="data")
    data_description = models.TextField()
    public = models.BooleanField(default=True)
    #contests = models.ManyToManyField(Contest,through="Contest_problem")

    class Meta:
        db_table = "problem"