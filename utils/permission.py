from rest_framework import permissions
from account.models import User
from classes.models import Class

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

    def has_permission(self,request,view):
        privilege = request.user.privilge
        return privilege == 1




# username이라는 path variable이 존재 할 경우 사용가능
# 해당 username의 User가 해당 api를 호출한 user와 동일한 인물인지 확인
class IsRightUser(permissions.BasePermission):

    def has_permission(self, request, view):
        username = view.kwargs.get('username',None)
        try:
            if User.objects.get(username=username) == request.user:
                return True
            else:
                return False
        except User.DoesNotExist:
            return False

#그 class의 member인지 (student, prof , TA 다 된다)
"""class IsClassMember(permissions.BasePermission):

    def has_permission(self,request,view):
        user =request.user
        class_id = view.kwargs.get("class_id",None)
        try:
            classid = Class.objects.get(id=class_id)
            privilege = classid.class_user.get(class_id = class_id, username = user.username):
            return True"""



