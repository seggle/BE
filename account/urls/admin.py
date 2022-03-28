from django.urls import path
from django.contrib.auth import views as auth_views
from account.views.admin import (
    ListUsersView,
    AdminUserInfoView,
)

app_name = "admin_account"
urlpatterns = [
    path('',ListUsersView.as_view() ),
    path('<username>/',AdminUserInfoView.as_view(),)
]