from django.db import models

# Create your models here.
class File(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.TextField()

    class Meta:
        db_table = "file"