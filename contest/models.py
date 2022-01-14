from ipaddress import ip_address
from django.db import models
from account.models import User
from classes.models import Class
from problem.models import Problem

# Create your models here.
class Contest(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_name="class_id")
    name = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_exam = models.BooleanField(default=False)
    users = models.ManyToManyField(User,through="Exam")

    class Meta:
        db_table = "contest"
    
    
    
# user - contest(exam) 다대다 테이블
class Exam(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_name="user_id")
    ip_address = models.TextField()
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE, db_name="contest_id")
    start_time = models.DateTimeField()
    exception =  models.BooleanField(default=False)
    
    class Meta:
        db_table = "exam"
