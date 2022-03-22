from django.db import models
from account.models import User
from problem.models import Problem

class Competition(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = "competition"

    def __str__(self):
        return self.id

class CompetitionUser(models.Model): # 0315
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column="competition")
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    is_show = models.BooleanField(default=True)
    privilege = models.IntegerField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "competition_user"