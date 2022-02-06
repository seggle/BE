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
    contests = models.ManyToManyField(Contest, through="Contest_problem", null=True,blank=True)

    # 삭제되었는지
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "problem"

#contest와 problem사이의 다대다 테이블
class Contest_problem(models.Model):
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest_id")
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id")
    title = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    order = models.IntegerField()