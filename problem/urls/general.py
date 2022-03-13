from django.urls import path, include
from problem.views.general import ProblemView, ProblemDetailView, ProblemVisibilityView, ProblemDataDownloadView


app_name = "problem"

urlpatterns = [
    path('',ProblemView.as_view()),
    path('<int:problem_id>/',ProblemDetailView.as_view()),
    path('<int:problem_id>/check',ProblemVisibilityView.as_view()),
    path('<int:problem_id>/download/data',ProblemDataDownloadView.as_view()),
    path('<int:problem_id>/download/solution',ProblemDataDownloadView.as_view()),
]