from django.urls import path
from competition.views.general import (
    CompetitionTaView,
    CompetitionUserView,
    CompetitionView,
    CompetitionDetailView,
    CompetitionProblemConfigurationView, CompetitionProblemOrderView, CompetitionCheckView
)

app_name = "competition"
urlpatterns = [
    path('', CompetitionView.as_view(), name="competition"),
    path('<int:competition_id>/', CompetitionDetailView.as_view(), name="competition_detail"),
    path('<int:competition_id>/check/', CompetitionCheckView.as_view(), name="competition_check"),
    path('<int:competition_id>/config/', CompetitionProblemConfigurationView.as_view(), name="manage_problems"),
    path('<int:competition_id>/order/', CompetitionProblemOrderView.as_view(), name="manage_problems"),
    path('<int:competition_id>/participation/', CompetitionUserView.as_view(), name='competition_user'),
    path('<int:competition_id>/participation/ta/', CompetitionTaView.as_view(), name='competition_ta'),
    # path('<int:competition_id>/<int:com_p_id>/', CompetitionProblemView.as_view(), name='competition_problem'),
    # path('<int:competition_id>/<int:com_p_id>/submission/', SubmissionCompetitionView.as_view(),
    #      name='competition_submission'),
    # path('<int:competition_id>/<int:com_p_id>/submissions/', SubmissionCompetitionListView.as_view(),
    #     name='competition_submission_list'),
    # path('<int:competition_id>/submissions/download/', SubmissionCompetitionDownloadView.as_view(),
    #      name='competition_submission_download'),
    # path('<int:competition_id>/<int:com_p_id>/check/', SubmissionCompetitionCheckView.as_view(),
    #      name='competition_leaderboard_check'),
]
