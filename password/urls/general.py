from django.urls import path, include
from django.contrib.auth import views as auth_views
from ..views.general import ApplyResetPasswordView, ResetPasswordView, ResetPasswordTokenView

urlpatterns = [
    path('reset_password_token_vaild/', ResetPasswordTokenView.as_view(), name='reset_password_token_vaild'),
    path('apply_reset_password/', ApplyResetPasswordView.as_view(), name='apply_reset_password_api'),
    path("reset_password/", ResetPasswordView.as_view(), name="reset_password_api"),
]