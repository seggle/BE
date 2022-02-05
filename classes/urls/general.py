from django.urls import path
from classes.views.general import (
    ClassView, ClassUserInfoView, ClassStdView, ClassTaView, 
)

app_name = "class"
urlpatterns = [
    path('', ClassView.as_view(), name="class_api"),
    path('<int:class_id>', ClassView.as_view()),
    path('<int:class_id>/users', ClassUserInfoView.as_view()), 
    path('<int:class_id>/std', ClassStdView.as_view()), 
    path('<int:class_id>/ta', ClassTaView.as_view()), 
]