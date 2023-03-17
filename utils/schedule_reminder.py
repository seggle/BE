from django.core.mail import send_mail
from django_crontab import CrontabCommand, Schedule
from datetime import datetime, timedelta

from competition.models import Competition
from competition.models import CompetitionUser
from account.models import User


def send_reminder_emails():
    now = datetime.now()
    one_day_later = now + timedelta(days=1)

    competitions_1day_left = Competition.objects.filter(end_time__lte=one_day_later, end_time__gt=now)

    for competition in competitions_1day_left:
        user_list = CompetitionUser.objects.filter(competition_id=competition.id)
        email_list = list(User.objects.filter(id__in=user_list.values('username').values_list('username__email', flat=True)))
        competition_title = competition.title
        #  대회에 참가한 user에게 reminder email을 보낸다

        # Calculate the reminder message
        subject = 'seggle 대회 마감 하루 전 알림 메일'
        message = f"참가하신 seggle 대회 [{competition_title}]가 내일 종료됩니다. 기한 내 결과물을 제출해주시길 바랍니다."
        # Send the email
        send_mail(
            subject,
            message,
            'noreply@example.com',
            [email_list],
            fail_silently=False,
        )