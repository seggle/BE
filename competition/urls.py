from django.urls import path
from competition.views import (
    CompetitionView,
    CompetitionDetailView,
)

app_name = "competition"
urlpatterns = [
    path('', CompetitionView.as_view()),
    path('<int:competition_id>/', CompetitionDetailView.as_view()),
]