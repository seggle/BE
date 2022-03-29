from django.db import models
from classes.models import Class
from problem.models import Problem

class ActiveModelQuerySet(models.QuerySet):

    def not_active(self, *args, **kwargs):
        return self.filter(is_deleted=True, *args, **kwargs)

    def active(self, *args, **kwargs):
        return self.filter(is_deleted=False, *args, **kwargs)

class Contest(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_id")
    name = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_exam = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    objects = ActiveModelQuerySet().as_manager()

    def __str__(self):
        return self.id

    class Meta:
        db_table = "contest"


# contest와 problem사이의 다대다 테이블
class ContestProblem(models.Model):
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest_id")
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id", related_name="problems")
    title = models.TextField()
    description = models.TextField()
    data_description = models.TextField()
    order = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    objects = ActiveModelQuerySet().as_manager()
    
    def __str__(self):
        return self.id

    class Meta:
        db_table = "contest_problem"
