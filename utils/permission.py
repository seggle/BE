from rest_framework import permissions

from account.models import User
from classes.models import Class, Class_user
from problem.models import Problem
from contest.models import Contest,Contest_problem


class CustomPermissionMixin(object):

    # user-privilege 교수 권한 확인
    def check_professor(self, privilege):
        if privilege == 1:
            return True
        else:
            return False

    # user-privilege 학생 권한 확인
    def check_student(self, privilege):
        if privilege == 0:
            return True
        else:
            return False


####
class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        privilege = request.user.privilege
        return privilege == 2


class IsProf(permissions.BasePermission):

    def has_permission(self, request, view):
        privilege = request.user.privilge
        return privilege == 1


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
        if Class_user.objects.filter(username=user.username, privilege=1).count():
            return True
        else:
            return False

class IsProblemOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self,request,view):
        problem = Problem.objects.get(id=view.kwargs.get('problem_id',None))

        return request.method in permissions.SAFE_METHODS \
               or problem.professr == request.user \
               or problem.created_user == request.user



"""# 그 class의 member인지 (student, prof , TA 다 된다)
class IsClassMember(permissions.BasePermission):

    def has_permission(self,request,view):
        user =request.user
        class_id = view.kwargs.get("class_id",None)
        problem_id = view.kwargs.get("problem_id",None)
        cp_id = view.kwargs.get("cp_id",None)
        if class_id:
            classid = Class.objects.get(id=class_id)
        elif cp_id:
            cp = Contest_problem.objects.get(id=cp_id).contest_id_set
        else:
            problem =


        try:
            classid = Class.objects.get(id=class_id)
            privilege =
            return True"""
