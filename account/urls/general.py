from tokenize import Token
from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views.general import (
    ChangePasswordView, LogoutView, UserRegisterView, LogoutAllView,UserInfoView
)

#simple-jwt
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "account"
urlpatterns = [
    path('', UserRegisterView.as_view()),
    path('<user_id>/',UserInfoView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
    path('change-password/', ChangePasswordView.as_view(), name='change password')
]