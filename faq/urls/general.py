from django.urls import path
from faq.views.general import (
    FaqView,
)

app_name = "faq"
urlpatterns = [
    path('', FaqView.as_view(), name="faq_api"),
]