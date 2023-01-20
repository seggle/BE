from rest_framework import serializers
from classes.models import Class, ClassUser


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        # fields = "__all__"
        fields = ["id", "name", "year", "semester", "created_user"]


class ClassGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "name", "year", "semester"]


class ClassPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["name", "year", "semester"]


class ClassUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassUser
        fields = ["class_id", "username", "is_show", "privilege"]


class ClassUserGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassUser
        fields = ["username", "privilege"]


class ClassUserGetInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassUser
        fields = ["class_id", "privilege"]