from tokenize import Token
from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views.general import (
    LogoutView, UserRegisterView, UserInfoView, # LogoutAllView
)

#simple-jwt
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "account"
urlpatterns = [
    path('', UserRegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('<username>/', UserInfoView.as_view(), name='user_info_api'),
    # path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
]