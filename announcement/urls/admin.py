from django.urls import path
from announcement.views.admin import (
    AnnouncementAdminAPI, AnnouncementDetailAdminAPI, AnnouncementCheckAdminAPI,
)

app_name = "admin_announcement"
urlpatterns = [
    path('', AnnouncementAdminAPI.as_view(), name="announcement_admin_api"),
    path('/<int:pk>', AnnouncementDetailAdminAPI.as_view(), name="announcement_detail_admin_api"),
    path('/<int:pk>/check', AnnouncementCheckAdminAPI.as_view(), name="announcement_check_api"),
]