from django.urls import path
from announcement.views.general import (
    AnnouncementView, AnnouncementDetailView,
)

app_name = "announcement"
urlpatterns = [
    path('', AnnouncementView.as_view(), name="announcement_api"),
    path('<int:pk>', AnnouncementDetailView.as_view(), name="announcement_detail_api"),
]