from django.db import models
from account.models import User
from competition.models import Competition
from problem.models import Problem
from classes.models import Class
from contest.models import Contest, ContestProblem
from utils.common import upload_to_submission

# Create your models here.

class Path(models.Model):
    path = models.TextField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = "path"

class SubmissionClass(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    path = models.ForeignKey(Path, on_delete=models.CASCADE, db_column="path")
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_id")
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest_id")
    c_p_id = models.ForeignKey(ContestProblem, on_delete=models.CASCADE, db_column="c_p_id")
    csv = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    ipynb = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id")
    score = models.FloatField(null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.TextField(null=True)
    on_leaderboard = models.BooleanField(default=False)
    status = models.IntegerField(default=0) # 0이면 문제 없음 , 1이면 에러 발생

    def __str__(self):
        return self.id

    class Meta:
        db_table = "submission_class"

class SubmissionCompetition(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    path = models.ForeignKey(Path, on_delete=models.CASCADE, db_column="path")
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column="competition_id")
    csv = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    ipynb = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id")
    score = models.FloatField(null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.TextField(null=True)
    on_leaderboard = models.BooleanField(default=False)
    status = models.IntegerField(default=0) # 0이면 문제 없음 , 1이면 에러 발생

    def __str__(self):
        return self.id

    class Meta:
        db_table = "submission_competition"