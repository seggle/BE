from django.db import models
from account.models import User
from problem.models import Problem

class ActiveModelQuerySet(models.QuerySet):

    def not_active(self, *args, **kwargs):
        return self.filter(is_deleted=True, *args, **kwargs)

    def active(self, *args, **kwargs):
        return self.filter(is_deleted=False, *args, **kwargs)

class Competition(models.Model):
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE, db_column="problem_id")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)
    objects = ActiveModelQuerySet().as_manager()
    
    def __str__(self):
        return self.id

    class Meta:
        db_table = "competition"

class CompetitionUser(models.Model):
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column="competition_id")
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    is_show = models.BooleanField(default=True)
    privilege = models.IntegerField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "competition_user"
