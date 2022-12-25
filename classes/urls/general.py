from django.urls import path
from classes.views.general import (

    ClassView, ClassDetailView, ClassStdView, ClassTaView, 

)
from contest.views import (
    ContestView, ContestCheckView, ContestProblemView, ContestProblemOrderView, ContestProblemTitleDescptView,
    ContestProblemInfoView,
)

from submission.views import (
    SubmissionClassView, SubmissionClassCheckView, SubmissionClassDownloadAllView,
    SubmissionClassDownloadLatestView, SubmissionClassDownloadHighestView,
    # SubmissionClassPerProblemListView,
)

app_name = "class"
urlpatterns = [
    # class
    path('', ClassView.as_view(), name="class_api"),
    path('<int:class_id>/', ClassDetailView.as_view()),
    path('<int:class_id>/std/', ClassStdView.as_view()), 
    path('<int:class_id>/ta/', ClassTaView.as_view()),

    # contest
    path('<int:class_id>/contests/', ContestView.as_view(), name="contest_api"),
    path('<int:class_id>/contests/<int:contest_id>/', ContestProblemView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/order/', ContestProblemOrderView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/description/', ContestProblemTitleDescptView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/check/', ContestCheckView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/', ContestProblemInfoView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/check/', SubmissionClassCheckView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/submission/', SubmissionClassView.as_view()),

    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/submissions/download/all/',
         SubmissionClassDownloadAllView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/submissions/download/latest/',
         SubmissionClassDownloadLatestView.as_view()),
    path('<int:class_id>/contests/<int:contest_id>/<int:cp_id>/submissions/download/highest/',
         SubmissionClassDownloadHighestView.as_view()),

]
