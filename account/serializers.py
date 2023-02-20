from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from competition.models import Competition
from classes.serializers import ClassUserGetInfoSerializer
from competition.serializers import CompetitionUserGetInfoSerializer
from classes.models import ClassUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = "__all__"
        fields = ["id", "username", "email", "name", "privilege", "is_active", "is_admin", "is_staff", "is_superuser",
                  "date_joined", "reset_password_token", "reset_password_token_expire_time"]


# 유저 회원가입
class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "name", "email", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True}
        }


# admin 00-00
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'name', 'privilege', 'date_joined', 'is_active']


class UserModifySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['privilege']


class UserInfoClassCompetitionSerializer(serializers.ModelSerializer):
    classes = ClassUserGetInfoSerializer(many=True)
    competition = CompetitionUserGetInfoSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'name', 'privilege', 'date_joined', 'is_active', 'classes', 'competition']


class ContributionsSerializer(serializers.Serializer):
    date = serializers.CharField()
    count = serializers.IntegerField()


class UserCompetitionSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    user_total = serializers.IntegerField()
    rank = serializers.IntegerField()

    class Meta:
        model = Competition
        fields = ['id', "title", "start_time", "end_time", "user_total", "rank"]


class UserClassPrivilege(serializers.ModelSerializer):
    class Meta:
        model = ClassUser
        fields = ['privilege']


class UserGetClassInfo(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    year = serializers.IntegerField()
    semester = serializers.IntegerField()
    privilege = serializers.IntegerField()
    is_show = serializers.BooleanField()


class TokenObtainResultSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super(TokenObtainResultSerializer, self).validate(attrs)
        data['username'] = self.user.username

        return data

class LoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["username", "password"]
