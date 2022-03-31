from rest_framework import permissions

from account.models import User
from classes.models import Class, ClassUser
from problem.models import Problem
from contest.models import Contest, ContestProblem
from competition.models import Competition, CompetitionUser


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        privilege = request.user.privilege
        return privilege == 2


class IsProf(permissions.BasePermission):

    def has_permission(self, request, view):
        privilege = request.user.privilege
        return privilege == 1


class IsProfAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
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

    def has_permission(self, request, view):
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

    def has_permission(self, request, view):
        user = request.user
        if ClassUser.objects.filter(username=user.username, privilege=1).count():
            return True
        else:
            return False


class IsProblemOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        problem = Problem.objects.get(id=view.kwargs.get('problem_id', None))

        return request.method in permissions.SAFE_METHODS \
               or problem.professor == request.user \
               or problem.created_user == request.user


class IsProblemOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        problem = Problem.objects.get(id=view.kwargs.get('problem_id', None))

        return problem.professor == request.user or problem.created_user == request.user


# 해당 클래스에 속하는지
class IsClassUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        class_id = view.kwargs.get('class_id', None)
        if not class_id:
            problem_id = view.kwargs.get('problem_id', None)
            if not problem_id:
                return False
            else:
                class_id = Problem.objects.get(id=problem_id).class_id.id
        class_query = ClassUser.objects.filter(username=user, class_id=class_id)
        if class_query.exists():
            return True
        else:
            return False


class ClassProfTAorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
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
    def has_permission(self, request, view):
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
    def has_permission(self, request, view):
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


class IsClassProfOrTA(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
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
    def has_permission(self, request, view):
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


class IsSafeMethod(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class IsCPUser(permissions.BasePermission):
    def has_permission(self, request, view):
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
    def has_permission(self, request, view):
        user = request.user
        competition_id = view.kwargs.get('competition_id', None)

        if CompetitionUser.objects.filter(username=user, competition_id=competition_id).exists():
            return True
        else:
            return False
