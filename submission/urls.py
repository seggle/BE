from django.urls import path

from submission.views import (
    SubmissionClassListView, SubmissionClassCsvDownloadView, SubmissionClassIpynbDownloadView, SubmissionCompetitionCsvDownloadView, SubmissionCompetitionIpynbDownloadView
)

app_name = "submission"
urlpatterns = [
    path('', SubmissionClassListView.as_view(), name="class_submission_list"),
    path('class/<int:submission_id>/download/csv/',SubmissionClassCsvDownloadView.as_view()),
    path('class/<int:submission_id>/download/ipynb/',SubmissionClassIpynbDownloadView.as_view()),
    path('competition/<int:submission_id>/download/csv/',SubmissionCompetitionCsvDownloadView.as_view()),
    path('competition/<int:submission_id>/download/ipynb/',SubmissionCompetitionIpynbDownloadView.as_view()),
]