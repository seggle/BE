from rest_framework import serializers
from .models import Contest, ContestProblem

class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ["id", "class_id", "name", "start_time", "end_time", "is_exam", "problems", "visible"]

class ContestGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ["id", "class_id", "name", "start_time", "end_time", "is_exam", "visible"]

class ContestPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ["name", "start_time", "end_time", "is_exam", "visible"]

class ContestProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestProblem
        fields = ["id", "contest_id", "problem_id", "title", "description", "data_description", "order"]

class ContestProblemDesSerializer(serializers.ModelSerializer):
    evaluation = serializers.CharField()

    class Meta:
        model = ContestProblem
        fields = ["title", "description", "data_description", "evaluation"]