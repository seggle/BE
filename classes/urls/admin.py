from django.urls import path
from classes.views.admin import (
    ClassAdminInfoView
)

app_name = "admin_class"
urlpatterns = [
    path('', ClassAdminInfoView.as_view(), name="class_admin_api"),
]