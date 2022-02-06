from rest_framework import serializers
from .models import User

class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

# 유저 회원가입
class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style = {"input_type": "password"}, write_only = True)

    class Meta:
        model = User
        fields = ["username","name","email","password","password2"]
        extra_kwargs = {
            "password" : {"write_only": True}
        }

    def save(self):
        user = User(
            email = self.validated_data["email"],
            username = self.validated_data["username"],
            name = self.validated_data['name'],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2 :
            raise serializers.ValidationError({'password': 'Passwords must match'})
        user.set_password(password)
        user.save()
        return user

#admin 00-00
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email','username','name','privilege', 'date_joined', 'is_active']

class UserModifySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['privilege']