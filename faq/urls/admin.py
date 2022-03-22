from django.urls import path
from faq.views.admin import (
    FaqAdminView, FaqCheckAdminView,
)

app_name = "admin_faq"
urlpatterns = [
    path('', FaqAdminView.as_view(), name="faq_admin_api"),
    path('<int:faq_id>', FaqAdminView.as_view()),
    path('check/', FaqCheckAdminView.as_view(), name="faq_check_api")
]