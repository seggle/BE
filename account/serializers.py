from rest_framework import serializers
from .models import User, ResetPassword


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# logout
# class UserLogoutSerializer(serializers.Serializer):

# 회원가입
class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "name", "email", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def save(self):
        user = User(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            name=self.validated_data['name'],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        user.set_password(password)
        user.save()
        return user


# 비밀번호 초기화
class ResetPasswordEmail(serializers.ModelSerializer):
    class Meta:
        model = ResetPassword
        fields = (
            'email',
        )


# 비밀번호 변경
class ChangePasswordSerializer(serializers.Serializer):
    model = User
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)


# 유저 정보
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'privilege', 'date_joined']
