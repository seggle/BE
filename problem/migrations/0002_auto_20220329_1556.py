# Generated by Django 3.1 on 2022-03-29 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='title',
            field=models.TextField(error_messages={'error': '중복된 제목 입니다.'}, unique=True),
        ),
    ]