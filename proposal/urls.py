from django.urls import path
from proposal.views import (
    ProposalView,
)

app_name = "proposal"
urlpatterns = [
    path('', ProposalView.as_view(), name="proposal_api"),
    path('<int:proposal_id>', ProposalView.as_view()) #User pk id가 전달되는 경우
    #path('<int:pk>', AnnouncementDetailAPI.as_view(), name="announcement_detail_api"),
]