from django.db import models
from classes.models import Class
from contest.models import Contest
from account.models import User


class Exam(models.Model):
    ip_address = models.CharField(null=True, max_length=50)  # ip 길이의 최대가 max_length이다
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username",db_column="user")
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_id")
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE, db_column="contest")
    exception = models.BooleanField(default=False)
    state = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "exam"
