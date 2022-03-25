from django.urls import path, include
from problem.views.admin import AdminProblemView

app_name = "admin_problem"

urlpatterns = [
    path('',AdminProblemView.as_view()),
]