from tokenize import Token
from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views import UserRegister

app_name = "account"
urlpatterns = [
    # 이메일로 password reset link를 발송할 수 있는 화면 (유저의 이메일 입력)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    # password_reset/ 에서 Reset my password 버튼을 누르면 나오는 화면
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    # 사용자에게 발송되는 링크 형식. 발송된 이메일의 링크를 누르면 비밀번호 변경할 수 있는 페이지 나옴
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    # password_reset_confirm/<uidb64>/<token>/ 에서 change my password 누르면 나오는 화면
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]