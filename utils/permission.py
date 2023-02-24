from typing import Any

from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.request import Request

from account.models import User
from classes.models import Class, ClassUser
from problem.models import Problem
from contest.models import Contest, ContestProblem
from competition.models import Competition, CompetitionUser, CompetitionProblem
from submission.models import *

from rest_framework.exceptions import NotFound


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False
        privilege = request.user.privilege
        return privilege == 2


class IsProf(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False
        privilege = request.user.privilege
        return privilege == 1


class IsProfAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            privilege = request.user.privilege
            if privilege == 0:
                return False
            else:
                return True


# username이라는 path variable이 존재 할 경우 사용가능
# 해당 username의 User가 해당 api를 호출한 user와 동일한 인물인지 확인
class IsRightUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False
        username = view.kwargs.get('username', None)
        try:
            if User.objects.get(username=username) == request.user:
                return True
            else:
                return False
        except User.DoesNotExist:
            return False


# 유저가 TA인지 검사 (어느 수업인지는 고려하지않음)
class IsTA(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        if ClassUser.objects.filter(username=user.username, privilege=1).count():
            return True
        else:
            return False


class IsProblemOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        problem = Problem.objects.filter(id=view.kwargs.get('problem_id')).first()
        if problem is None:
            return False
        return request.method in permissions.SAFE_METHODS \
            or problem.professor == request.user \
            or problem.created_user == request.user


class IsProblemOwner(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        problem = Problem.objects.get(id=view.kwargs.get('problem_id', None))

        return problem.professor == request.user or problem.created_user == request.user


# 해당 클래스에 속하는지
class IsClassUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        # Change due to model modification in Problem model
        class_id = view.kwargs.get('class_id', None)
        if not class_id:
            contest_id = view.kwargs.get('contest_id', None)
            if not contest_id:
                return False
            else:
                class_id = Contest.objects.get(contest_id=contest_id).class_id.id
        class_query = ClassUser.objects.filter(username=user, class_id=class_id)
        if class_query.exists():
            return True
        else:
            return False


class ClassProfTAorReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        class_id = view.kwargs.get('class_id', None)
        if not class_id:
            return False
        try:
            if ClassUser.objects.get(username=user, class_id=class_id).privilege == 0:
                return False
            else:
                return True
        except:
            return False


class ClassProfOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        class_id = view.kwargs.get('class_id', None)
        if not class_id:
            return False
        try:
            if ClassUser.objects.get(username=user, class_id=class_id).privilege == 2:
                return True
            else:
                return False
        except:
            return False


class IsClassProf(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        class_id = view.kwargs.get('class_id', None)
        if not class_id:
            return False
        try:
            if ClassUser.objects.get(username=user, class_id=class_id).privilege == 2:
                return True
            else:
                return False
        except:
            return False


class IsClassProfOrTA(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        class_id = view.kwargs.get('class_id', None)
        if not class_id:
            return False
        try:
            if ClassUser.objects.get(username=user, class_id=class_id).privilege == 0:
                return False
            else:
                return True
        except:
            return False


class IsCompetitionManagerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            user = request.user
            competition_id = view.kwargs.get('competition_id', None)
            if not competition_id:
                return False
            try:
                if CompetitionUser.objects.get(username=user, competition_id=competition_id).privilege == 0:
                    return False
                else:
                    return True
            except:
                return False


class IsCompetitionProfOrTA(permissions.BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        user = request.user
        competition_id = view.kwargs.get('competition_id', None)

        if competition_id is None:
            return False
        try:
            if CompetitionUser.objects.get(username=user, competition_id=competition_id).privilege > 0:
                return True
            else:
                return False
        except:
            return False


class IsSafeMethod(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class IsSafeMethodCompetition(permissions.BasePermission):
    def has_permission(self, request: Request, view: Any):
        if isinstance(request.user, AnonymousUser):
            return False

        competition_id = view.kwargs.get('competition_id', None)

        if not CompetitionUser.objects.filter(username=request.user.username,
                                              competition_id=competition_id).exists():
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class IsSafeMethodClass(permissions.BasePermission):
    def has_permission(self, request: Request, view: Any):
        if isinstance(request.user, AnonymousUser):
            return False

        class_id = view.kwargs.get('class_id', None)

        if not ClassUser.objects.filter(username=request.user.username,
                                        class_id=class_id).exists():
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class IsCPUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        if isinstance(request.user, AnonymousUser):
            return False

        cp_id = view.kwargs.get('cp_id', None)

        if not cp_id:
            return False
        else:
            try:
                class_id = ContestProblem.objects.get(id=cp_id).contest_id.class_id.id
                if ClassUser.objects.filter(username=request.user, class_id=class_id).exists():
                    return True
                else:
                    return False
            except:
                pass


class IsCompetitionUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        competition_id = view.kwargs.get('competition_id', None)

        if CompetitionUser.objects.filter(username=user, competition_id=competition_id).exists():
            return True
        else:
            return False


class IsProblemDownloadableUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        problem_id = view.kwargs.get('problem_id', None)

        try:
            problem = Problem.objects.get(id=problem_id)
        except:
            return False

        contest_problems = ContestProblem.objects.filter(problem_id=problem_id)
        competition_problems = CompetitionProblem.objects.filter(problem_id=problem_id)

        # Professor and created_user only
        if contest_problems.count() == 0 and competition_problems.count() == 0:
            return True if problem.professor == user or problem.created_user == user else False

        # People who involved in competition or class where the problem is existed
        if contest_problems.count() > 0:
            classes = set(contest_problems.order_by('contest_id__class_id_id') \
                                .distinct() \
                                .values_list('contest_id__class_id_id', flat=True))

            user_classes = set(ClassUser.objects.filter(username=user.username)
                               .order_by('class_id_id')
                               .distinct()
                               .values_list('class_id_id', flat=True))

            return False if len(classes.intersection(user_classes)) == 0 else True

        if competition_problems.count() > 0:

            eligible_problems = competition_problems.filter(competition_id__competitionuser__username=user.username)
            return False if eligible_problems.count() == 0 else True


# 수업의 조교 , 수업의 prof , 제출한 사람
class IsSubClassDownloadableUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        submission_id = view.kwargs.get('submission_id', None)

        try:
            class_sub = SubmissionClass.objects.get(id=submission_id)
        except:
            return False

        if user == class_sub.username:
            return True

        class_ = class_sub.class_id
        prof = class_.created_user
        if user == prof:
            return True

        if ClassUser.objects.get(username=user, class_id=class_.id).privilege == 1:
            return True
        return False


# 대회 조교 대회 생성자 , 제출한 사람
class IsSubCompDownloadableUser(permissions.BasePermission):

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        if isinstance(user, AnonymousUser):
            return False

        submission_id = view.kwargs.get('submission_id', None)

        try:
            comp_sub = SubmissionCompetition.objects.get(id=submission_id)
        except:
            return False

        if user == comp_sub.username:
            return True

        competition = comp_sub.competition_id

        try:
            privilege = CompetitionUser.objects.get(username=user, competition_id=competition.id).privilege
            if privilege == 1 or privilege == 2:
                return True
            else:
                return False
        except:
            return False
