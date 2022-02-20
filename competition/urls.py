from django.urls import path
from competition.views import (
    CompetitionTaView,
    CompetitionUserView,
    CompetitionView,
    CompetitionDetailView,
)
from submission.views import (
    SubmissionCompetitionView,
)

app_name = "competition"
urlpatterns = [
    path('', CompetitionView.as_view(), name="competition"),
    path('<int:competition_id>/', CompetitionDetailView.as_view(), name="competition_detail"),
    path('<int:competition_id>/participation/', CompetitionUserView.as_view(), name='competition_user'),
    path('<int:competition_id>/participation/ta', CompetitionTaView.as_view(), name='competition_ta'),
    path('<int:competition_id>/<str:username>/', SubmissionCompetitionView.as_view(), 'competition_submission'),
]