from rest_framework import permissions
from account.models import User
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
class Is_Admin(permissions.BasePermission):

    def has_permission(self, request, view):
        privilege = request.user.privilege
        return privilege == 2

class Is_Prof(permissions.BasePermission):
    pass

class Is_Right_User(permissions.BasePermission):

    def has_permission(self,request,view):
        username = view.kwargs.get('username',None)
        print(username)
        if User.objects.get(username=username) == request.user:
            return True
        else:
            return False
