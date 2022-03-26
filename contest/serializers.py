from rest_framework import serializers
from .models import Contest, ContestProblem
from problem.models import Problem

class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        # fields = "__all__"
        fields = ["id", "class_id", "name", "start_time", "end_time", "is_exam", "visible"]

class ContestPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ["name", "start_time", "end_time", "is_exam", "visible"]

class ContestProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestProblem
        fields = ["id", "contest_id", "problem_id", "title", "description", "data_description", "order"]

class ContestProblemPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestProblem
        fields = ["contest_id", "problem_id", "title", "description", "data_description", "order"]

class ContestProblemDesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestProblem
        fields = ["title", "description", "data_description"]

class ContestProblemDesEvaluateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["evaluation"]