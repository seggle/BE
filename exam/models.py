from django.db import models
from contest.models import Contest
from account.models import User


class Exam(models.Model):
    ip_address = models.CharField(max_length=50)  # ip 길이의 최대가 max_length이다
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username",db_column="user")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, db_column="contest")
    exception = models.BooleanField(null=True, blank=True, default=False)
    start_time = models.DateTimeField(auto_now_add=True)
    is_duplicated = models.BooleanField(default = False)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "exam"
