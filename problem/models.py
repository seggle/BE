from django.db import models
from account.models import User
from classes.models import Class
from utils.common import upload_to_data, upload_to_solution
from utils.message import *

class ActiveModelQuerySet(models.QuerySet):

    def not_active(self, *args, **kwargs):
        return self.filter(is_deleted=True, *args, **kwargs)

    def active(self, *args, **kwargs):
        return self.filter(is_deleted=False, *args, **kwargs)


class Problem(models.Model):
    title = models.TextField(unique=True, error_messages=msg_problem_model_title_unique)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user",to_field="username",related_name="problem")
    data = models.FileField(blank=True,upload_to=upload_to_data)
    solution = models.FileField(blank=True,upload_to=upload_to_solution)
    data_description = models.TextField()
    public = models.BooleanField(default=False)
    evaluation = models.TextField() # 평가 방식
    class_id = models.ForeignKey(Class, on_delete = models.CASCADE , db_column="class", blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, db_column="professor",to_field="username",related_name="problem_professor", blank=True, null=True)
    objects = ActiveModelQuerySet().as_manager()

    def __str__(self):
        return self.id

    class Meta:
        db_table = "problem"