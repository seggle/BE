
from django.urls import path
from django.contrib.auth import views as auth_views
from exam.views import (
    ExamExceptionView,ExamParticipateView,ExamResetView
)



app_name = "exam"
urlpatterns = [
    path('', ExamParticipateView.as_view()),
    path('<int:exam_id>/exception/',ExamExceptionView.as_view()),
    path('<int:exam_id>/reset/',ExamResetView.as_view()),
]