from rest_framework import serializers
from .models import Contest, Contest_problem

class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        # fields = "__all__"
        fields = ["id", "class_id", "name", "start_time", "end_time", "is_exam", "problems", "visible"]

class ContestGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ["id", "class_id", "name", "start_time", "end_time", "is_exam", "visible"]

class ContestProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest_problem
        # fields = "__all__"
        fields = ["id", "contest_id", "problem_id", "title", "description", "data_description", "order"]

# class ClassAdminGetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Class
#         #fields = "__all__"
#         fields = ["id", "name", "year", "semester", "created_user"]

# class Class_user_Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Class_user
#         fields = "__all__"

# class Class_user_Get_Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Class_user
#         fields = ["username", "privilege"]