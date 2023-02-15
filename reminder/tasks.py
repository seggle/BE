from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab

import pytz
import datetime
from django.core.mail import EmailMessage

from classes.models import ClassUser
from contest.models import Contest
from competition.models import Competition,CompetitionUser

logger = get_task_logger(__name__)

app = Celery()

@app.on_after_configure.connect
def reminder_email(sender, **kwargs):
    # Executes daily at 09:00 a.m.
    sender.add_periodic_task(
        crontab(minute=0, hour=9),
        send_reminder_email_contest(),
        send_reminder_email_competition()
)

@app.task
def send_reminder_email_contest():
    """
    Send Reminder email to Class Users the day before contest ends
    """

@app.task
def send_reminder_email_competition():
    """
    Send Reminder email to CompetitionUsers the day before competition ends
    """
