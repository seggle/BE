from rest_framework import serializers
from .models import Problem


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        # fields = "__all__"
        fields = ["id", "title", "description", "created_time", "created_user", "data", "solution", "data_description", "public", "evaluation", "is_deleted", "professor", "type"]


class ProblemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields =["id", "title", "description", "created_time", "created_user", "data_description", "evaluation", "public", "is_deleted"]


class ProblemPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["title", "description", "data_description", "evaluation", "public", "data", "solution"]


class AllProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["id", "title", "created_time", "created_user", "data", "solution", "public"]


class ProblemGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        exclude = ["created_time"]


class ProblemPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["title", "description", "data_description", "public", "evaluation"]


class ProblemPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["public"]
