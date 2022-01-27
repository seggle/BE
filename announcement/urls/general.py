from django.urls import path
from announcement.views.general import (
    AnnouncementAPI, AnnouncementDetailAPI,
)

app_name = "announcement"
urlpatterns = [
    path('', AnnouncementAPI.as_view(), name="announcement_api"),
    path('/<int:pk>', AnnouncementDetailAPI.as_view(), name="announcement_detail_api"),
]