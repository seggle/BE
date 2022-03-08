from django.urls import path, include
from django.contrib.auth import views as auth_views
from ..views.general import ApplyResetPasswordAPI, ResetPasswordAPI, ResetPasswordToken

urlpatterns = [
    path('reset_password_token_vaild/', ResetPasswordToken.as_view(), name='reset_password_token_vaild'),
    path('apply_reset_password/', ApplyResetPasswordAPI.as_view(), name='apply_reset_password_api'),
    path("reset_password/", ResetPasswordAPI.as_view(), name="reset_password_api"),

]