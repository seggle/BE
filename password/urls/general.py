from django.urls import path, include
from django.contrib.auth import views as auth_views
from ..views.general import ApplyResetPasswordAPI, ResetPasswordAPI, ResetPasswordToken

urlpatterns = [
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    # path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    # path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # path('request-reset-email/', Test.as_view(), name="request-reset-email"),
    # path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    # path('password-reset-complete', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),



    path('reset_password_token_vaild/', ResetPasswordToken.as_view(), name='reset_password_token_vaild'),
    path('apply_reset_password/', ApplyResetPasswordAPI.as_view(), name='apply_reset_password_api'),
    path("reset_password/", ResetPasswordAPI.as_view(), name="reset_password_api"),

]