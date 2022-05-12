from tokenize import Token
from django.urls import path
from django.contrib.auth import views as auth_views
from account.views.general import (
    LogoutView, UserCompetitionInfoView, UserRegisterView,
    UserInfoView, ClassInfoView, ObtainPairView, RefreshView, ContributionsView,UserClassPrivilege,UserCompetitionPrivilege
)


#simple-jwt
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "account"
urlpatterns = [
    path('', UserRegisterView.as_view()),
    path('login/', ObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', RefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('class/', ClassInfoView.as_view()),
    path('class/<int:class_id>/', UserClassPrivilege.as_view(), name="user_class_privilege"),
    path('competition/<int:competition_id>/', UserCompetitionPrivilege.as_view(),name="user_competition_privilege"),
    path('<str:username>/', UserInfoView.as_view(), name='user_info_api'),
    path('<str:username>/contributions/', ContributionsView.as_view(), name="user_contributions"),
    path('<str:username>/competitions/', UserCompetitionInfoView.as_view(), name='user_competition_info'),
    # path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
]
