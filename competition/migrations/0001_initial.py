# Generated by Django 3.1 on 2022-01-26 23:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('problem', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('problem_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='problem.problem')),
            ],
            options={
                'db_table': 'competition',
            },
        ),
        migrations.CreateModel(
            name='Competition_user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_show', models.BooleanField(default=True)),
                ('privilege', models.IntegerField()),
                ('competition_id', models.ForeignKey(db_column='competition_id', on_delete=django.db.models.deletion.CASCADE, to='competition.competition')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'competition_user',
            },
        ),
        migrations.AddField(
            model_name='competition',
            name='users',
            field=models.ManyToManyField(through='competition.Competition_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
