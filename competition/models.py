from django.db import models

from account.models import User
from problem.models import Problem

# Create your models here.
class Competition(models.Model):
    # problem이 만들어져야함!!
    # Competition하고 연결된 problem id를 의미함
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="user_id")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    users = models.ManyToManyField(User,through="Competition_user")

    class Meta:
        db_table = "competition"

#competition과 user를 연결하는 다대다 테이블
class Competition_user(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column="competition_id")
    is_show = models.BooleanField(default=True)
    privilege = models.IntegerField()

    class Meta:
        db_table = "competition_user"
