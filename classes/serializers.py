from rest_framework import serializers
from classes.models import Class, Class_user

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"

class ClassGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"
        #fields = ["name", "year", "semester", "created_user"]

class Class_user_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Class_user
        fields = "__all__"

class Class_user_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Class_user
        fields = ["username", "privilege"]