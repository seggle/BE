from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views.admin import (
    ListUsersView,
    AdminUserModifyView,
)

app_name = "admin_account"
urlpatterns = [
    path('',ListUsersView.as_view() ),
    path('<username>/',AdminUserModifyView.as_view(),)
]