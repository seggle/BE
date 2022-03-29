from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from utils.message import *

class UserManager(BaseUserManager):

    use_in_migrations = True # 모델 관리자 마이그레이션

    def create_user (self, username, email, name, password=None): # user 생성
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not name:
            raise ValueError("User must have a name")

        user = self.model(
            username = username,
            name = name,
            email = self.normalize_email(email), # @도메인 정규화
        )
        user.set_password(password) # 회원가입시 받은 비밀번호를 hash하여 저장하는 함수
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, email, password): # 관리자 유저 생성

        user = self.create_user(
            username = username,
            email = self.normalize_email(email),
            name = name,
            password = password
        )
        user.privilege = 2
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager() # 만들어진 쿼리셋 UserManager 상속

    username = models.CharField(max_length=20, unique=True, error_messages=msg_user_model_username_unique)
    email = models.EmailField(max_length=255, unique=True, error_messages=msg_user_model_email_unique)
    name = models.CharField(max_length=20, null=True)
    privilege = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True) # 유저 모델의 필수 필드
    is_admin = models.BooleanField(default=False) # 유저 모델의 필수 필드
    is_staff = models.BooleanField(default=False) # 유저 모델의 필수 필드
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    reset_password_token = models.CharField(max_length=50, null=True)
    reset_password_token_expire_time = models.DateTimeField(null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self): # 인스턴스 조회할 때 보여지는 이름 설정. 정의 안하면 <Queryset1>처럼 보임
        return self.username

    class Meta:
        db_table = "user"
