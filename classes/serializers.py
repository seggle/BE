from rest_framework import serializers
from classes.models import Class, Class_user

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        # fields = "__all__"
        fields = ["id", "name", "year", "semester", "created_user"]

class ClassGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        #fields = "__all__"
        fields = ["id", "name", "year", "semester"]

class ClassAdminGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        #fields = "__all__"
        fields = ["id", "name", "year", "semester", "created_user"]

class Class_user_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Class_user
        # fields = "__all__"
        fields = ["id", "class_id", "username", "is_show", "privilege"]

class Class_user_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Class_user
        fields = ["username", "privilege"]

class ClassUserGetInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class_user
        fields = ["class_id", "privilege"]