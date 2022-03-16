from django.db import models
from account.models import User

# Create your models here.

class Class_user(models.Model): # 0315
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, db_column="class_id")
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    is_show = models.BooleanField(default=True)
    privilege = models.IntegerField()

    class Meta:
        db_table = "class_user"

class Class(models.Model):
    name = models.TextField()
    year = models.IntegerField()
    semester = models.IntegerField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user", related_name='created_user', to_field="username")
    # 0315 is_deleteㅇ 넣기
    class Meta:
        db_table = "class"
