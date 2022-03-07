from django.db import models
from account.models import User
from classes.models import Class
from utils.common import upload_to_data, upload_to_solution

class Problem(models.Model):
    title = models.TextField(unique=True)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user",to_field="username",related_name="problem")
    # data = models.FileField(blank=True,null=True,upload_to="media/")
    data = models.FileField(blank=True,null=True,upload_to=upload_to_data)
    solution = models.FileField(blank=True,null=True,upload_to=upload_to_solution)
    data_description = models.TextField()
    public = models.BooleanField(default=False)
    evaluation = models.TextField() # 평가 방식
    # 어느 클래스에서 만들어 졌는지
    class_id = models.ForeignKey(Class, on_delete = models.CASCADE , db_column="class", blank=True, null=True)
    # 삭제되었는지
    is_deleted = models.BooleanField(default=False)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, db_column="professor",to_field="username",related_name="problem_professor", blank=True, null=True)

    class Meta:
        db_table = "problem"