from django.urls import path

from .views import (
    LeaderboardClassView,
    LeaderboardCompetitionView,
)

app_name = "leaderboard"
urlpatterns = [
    path('contest-problem/<int:cp_id>/', LeaderboardClassView.as_view(), name="class_leaderboard"),
    path('competitions/<int:competition_id>/', LeaderboardCompetitionView.as_view(), name="competition_leaderboard"),
]