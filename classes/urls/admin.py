from django.urls import path
from classes.views.admin import (
    ClassInfoView
)

app_name = "admin_class"
urlpatterns = [
    path('', ClassInfoView.as_view(), name="class_admin_api"),
]