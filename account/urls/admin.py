from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views.admin import (
    ListUsersAPI,
    AdminUserModifyAPI,
)

urlpatterns = [
    path('admin/users/',ListUsersAPI.as_view() ),
    path('admin/users/<user_id>/',AdminUserModifyAPI.as_view(),)
]