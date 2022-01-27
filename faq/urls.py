from django.urls import path
from faq.views import (
    FaqView,
)

app_name = "faq"
urlpatterns = [
    path('', FaqView.as_view(), name="faq_api"),
    path('<int:faq_id>', FaqView.as_view())
]