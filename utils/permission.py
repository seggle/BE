class CustomPermissionMixin(object):
    def check_professor(self, privilege):
        if privilege == 1:
            return True
        else:
            return False

    def check_student(self, privilege):
        if privilege == 0:
            return True
        else:
            return False