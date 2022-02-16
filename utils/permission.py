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