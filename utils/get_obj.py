from rest_framework.generics import get_object_or_404
from account.models import * 
from announcement.models import * 
from classes.models import *
from competition.models import *
from contest.models import *
from exam.models import *
from faq.models import *
from leaderboard.models import *
from problem.models import *
from proposal.models import *
from submission.models import *
from django.http import Http404

# is_deleted 고려해주세요ㅎㅎ사랑합니다~~~~

# faq
def get_faq(id):
    faq = get_object_or_404(Faq, id = id)
    return faq

# username
def get_username(username): 
    user = get_object_or_404(User, username=username)
    return user

# announcement
def get_announcement(id):
    announcement = get_object_or_404(Announcement, id = id)
    return announcement

# proposal
def get_proposal(id):
    proposal = get_object_or_404(Proposal, id = id)
    return proposal

# faq
def get_faq(id):
    faq = get_object_or_404(Faq, id = id)
    return faq

# class
def get_class(id):
    _class = get_object_or_404(Class, id = id)
    if _class.is_deleted:
        raise Http404()
    return _class

# competition
def get_competition(id):
    competition = get_object_or_404(Competition, id=id)
    if competition.is_deleted:
        raise Http404()
    problem = get_object_or_404(Problem, id=competition.problem_id.id)
    if problem.is_deleted:
        raise Http404()
    else:
        return competition

# problem
def get_problem(id):
    problem = get_object_or_404(Problem, id=id)
    if problem.is_deleted:
        raise Http404()
    return problem

# contest
def get_contest(id):
    contest = get_object_or_404(Contest, id = id)
    if contest.is_deleted:
        raise Http404()
    return contest

# contest_problem
def get_contest_problem(id):
    contestproblem = get_object_or_404(ContestProblem, id=id)
    if contestproblem.is_deleted:
        raise Http404()
    if contestproblem.problem_id.is_deleted:
        raise Http404()
    return contestproblem

def get_submission_class(id):
    class_submission = get_object_or_404(SubmissionClass, id=id)
    return class_submission

def get_submission_competition(id):
    competition_submission = get_object_or_404(SubmissionCompetition, id=id)
    return competition_submission

def get_exam(id):
    exam = get_object_or_404(Exam, id=id)
    return exam
