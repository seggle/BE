from django.db import models
from account.models import User
from competition.models import Competition
from problem.models import Problem
from classes.models import Class
from contest.models import Contest, Contest_problem
from utils.common import upload_to_submission

class Path(models.Model): # 0315
    path = models.TextField()

    def __str__(self):
        return self.id

    class Meta:
        db_table = "path"

class SubmissionClass(models.Model): # 0315
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    path = models.ForeignKey(Path, on_delete=models.CASCADE, db_column="path")
    class_ = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest")
    c_p = models.ForeignKey(Contest_problem, on_delete=models.CASCADE, db_column="c_p")
    csv = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    ipynb = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem")
    score = models.FloatField(null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.TextField(null=True)
    on_leaderboard = models.BooleanField(default=False) # 1이면 leaderboard에 보이고 0이면 보이지 않음
    status = models.IntegerField(default=0) # 0이면 문제 없음 , 1이면 에러 발생

    def __str__(self):
        return self.id

    class Meta:
        db_table = "submission_class"

class SubmissionCompetition(models.Model): # 0315
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    path = models.ForeignKey(Path, on_delete=models.CASCADE, db_column="path")
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column="competition_id")
    csv = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    ipynb = models.FileField(blank=True,null=True,upload_to=upload_to_submission)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem")
    score = models.FloatField(null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.TextField(null=True)
    on_leaderboard = models.BooleanField(default=False) # 1이면 leaderboard에 보이고 0이면 보이지 않음
    status = models.IntegerField(default=0) # 0이면 문제 없음 , 1이면 에러 발생

    def __str__(self):
        return self.id

    class Meta:
        db_table = "submission_competition"