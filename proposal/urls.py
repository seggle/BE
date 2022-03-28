from django.urls import path
from proposal.views import (
    ProposalView,
)

app_name = "proposal"
urlpatterns = [
    path('', ProposalView.as_view(), name="proposal_api"),
    path('<int:proposal_id>/', ProposalView.as_view())
]