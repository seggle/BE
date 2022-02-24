from django.urls import path

from .views import (
    LeaderboardClassView, 
)

app_name = "leaderboard"
urlpatterns = [
    path('contest-problem/<int:cp_id>', LeaderboardClassView.as_view(), name="class_leaderboard"),
]