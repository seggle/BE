from django.urls import path
from problem.views.admin import AdminProblemView

app_name = "admin_problem"

urlpatterns = [
    path('',AdminProblemView.as_view()),
]