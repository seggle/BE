from django.urls import path

from submission.views import (
    SubmissionClassListView, SubmissionClassCsvDownloadView, SubmissionClassIpynbDownloadView, SubmissionCompetitionCsvDownloadView, SubmissionCompetitionIpynbDownloadView
)

app_name = "submission"
urlpatterns = [
    path('', SubmissionClassListView.as_view(), name="class_submission_list"),
    path('class/<int:submission_id>/download/1',SubmissionClassCsvDownloadView.as_view()),
    path('class/<int:submission_id>/download/2',SubmissionClassIpynbDownloadView.as_view()),
    path('competition/<int:submission_id>/download/1',SubmissionCompetitionCsvDownloadView.as_view()),
    path('competition/<int:submission_id>/download/2',SubmissionCompetitionIpynbDownloadView.as_view()),
]