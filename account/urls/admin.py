from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views.admin import (
    ListUsersView,
    AdminUserModifyView,
)

urlpatterns = [
    path('',ListUsersView.as_view() ),
    path('<user_id>',AdminUserModifyView.as_view(),)
]