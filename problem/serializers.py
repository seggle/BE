from rest_framework import serializers
from .models import Problem


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = "__all__"

class AllProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["id","title","created_time","created_user","public","data"]

class ProblemGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        exclude = ["created_time"]

class ProblemPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["title","description","data_description","public"]

class ProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["id", "title", "created_time", "created_user", "public"]