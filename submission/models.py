from django.db import models
from account.models import User
from competition.models import Competition
from problem.models import Problem
from classes.models import Class
from contest.models import Contest_problem

# Create your models here.
class Submission(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column="competition_id", blank=True)
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id")
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_id", blank=True)
    c_p_id = models.ForeignKey(Contest_problem, on_delete=models.CASCADE, db_column="c_p_id", blank=True)
    status = models.IntegerField(default=0) # 0이면 문제 없음 , 1이면 에러 발생
    score = models.FloatField()
    csv = models.FileField(blank=True,null=True)
    ipynb = models.FileField(blank=True,null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.TextField(null=True)
    on_leaderboard = models.BooleanField(default=False) # 1이면 leaderboard에 보이고 0이면 보이지 않음