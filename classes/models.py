from django.db import models
from account.models import User

# Create your models here.
class Class(models.Model):
    name = models.TextField()
    semester = models.TextField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_name="created_user")
    users = models.ManyToManyField(User,through="Class_user")

    class Meta:
        db_table = "class"

class Class_user(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class_id")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    is_show = models.BooleanField(default=True)
    privilege = models.IntegerField()

    class Meta:
        db_table = "class_user"