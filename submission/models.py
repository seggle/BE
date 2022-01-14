from django.db import models
from account.models import User
from competition.models import Competition
from problem.models import Problem
from classes.models import Class
from contest.models import Contest_problem
from file.models import File

# Create your models here.
class Submission(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_name="user_id")
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE, db_name="competition_id")
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_name="problem_id")
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_name="class_id")
    c_p_id = models.ForeignKey(Contest_problem, on_delete=models.CASCADE, db_name="c_p_id")
    status = models.IntegerField() # 0이면 문제 없음 , 1이면 에러 발생
    score = models.FloatField()
    csv = models.ForeignKey(File)
    ipynb = models.ForeignKey(File)
    created_time = models.DateTimeField()
    ip_address = models.TextField()
    on_leaderboard = models.BooleanField() # 1이면 leaderboard에 보이고 0이면 보이지 않음