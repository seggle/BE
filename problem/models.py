from django.db import models
from contest.models import Contest
from account.models import User
from file.models import File



class Problem(models.Model):
    title = models.TextField()
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user",to_field="username",null=True,blank=True)
    data = models.FileField(blank=True,null=True,upload_to="media/")
    solution = models.FileField(blank=True,null=True,upload_to="solution/")
    data_description = models.TextField()
    public = models.BooleanField(default=True)


    # 삭제되었는지
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "problem"
