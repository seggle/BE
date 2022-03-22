from django.db import models
from account.models import User

# Create your models here.

class ClassUser(models.Model):
    class_ = models.ForeignKey('Class', on_delete=models.CASCADE, db_column="class_")
    username = models.ForeignKey(User, on_delete=models.CASCADE, db_column="username", to_field="username")
    is_show = models.BooleanField(default=True)
    privilege = models.IntegerField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "class_user"

class Class(models.Model):
    name = models.TextField()
    year = models.IntegerField()
    semester = models.IntegerField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="created_user", related_name='created_user', to_field="username")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "class"
