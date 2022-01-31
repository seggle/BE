from django.urls import path
from classes.views import (
    ClassView, ClassUserView,
)

app_name = "class"
urlpatterns = [
    path('', ClassView.as_view(), name="class_api"), 
    path('<int:class_id>', ClassView.as_view()), 
    path('<int:class_id>/users', ClassUserView.as_view())
]