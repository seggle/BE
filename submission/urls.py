from django.urls import path

from submission.views import (
    SubmissionClassListView, 
)

app_name = "submission"
urlpatterns = [
    path('', SubmissionClassListView.as_view(), name="class_submission_list"),
]