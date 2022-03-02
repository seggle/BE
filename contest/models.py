from ipaddress import ip_address
from django.db import models
from account.models import User
from classes.models import Class
from problem.models import Problem


class Contest(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_id")
    name = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_exam = models.BooleanField(default=False)
    problems = models.ManyToManyField('Contest_problem', related_name="contests", blank=True)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = "contest"


# contest와 problem사이의 다대다 테이블
class Contest_problem(models.Model):
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest_id")
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id")
    title = models.TextField()
    description = models.TextField()
    data_description = models.TextField()
    order = models.IntegerField()

    class Meta:
        db_table = "contest_problem"
