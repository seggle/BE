from django.db import models
from contest.models import Contest
from account.models import User


class Exam(models.Model):
    ip_address = models.CharField(max_length=50)  # ip 길이의 최대가 max_length이다
    username = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username", db_column="username")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest")
    exception = models.BooleanField(null=True, blank=True, default=False) # 0315
    start_time = models.DateTimeField(auto_now_add=True)
    is_duplicated = models.BooleanField(default = False)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "exam"
