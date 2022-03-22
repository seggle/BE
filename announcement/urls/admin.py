from django.urls import path
from announcement.views.admin import (
    AnnouncementAdminView, AnnouncementDetailAdminView, AnnouncementCheckAdminView,
)

app_name = "admin_announcement"
urlpatterns = [
    path('', AnnouncementAdminView.as_view(), name="announcement_admin_api"),
    path('<int:announcement_id>', AnnouncementDetailAdminView.as_view(), name="announcement_detail_admin_api"),
    path('<int:announcement_id>/check', AnnouncementCheckAdminView.as_view(), name="announcement_check_api"),
]