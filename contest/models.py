from ipaddress import ip_address
from django.db import models
from account.models import User
from classes.models import Class
from problem.models import Problem


class Contest(models.Model):
    class_ = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_")
    name = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_exam = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "contest"

class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem")
    title = models.TextField()
    description = models.TextField()
    data_description = models.TextField()
    order = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.id

    class Meta:
        db_table = "contest_problem"
