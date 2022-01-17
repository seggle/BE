from tokenize import Token
from django.urls import path, include

urlpatterns = [
   path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]