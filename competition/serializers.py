from rest_framework import serializers
from .models import Competition
from problem.models import Problem
from problem.serializers import ProblemSerializer

class CompetitionGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['problem_id', 'id', 'start_time', 'end_time']


class CompetitionDetailSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)
    class Meta:
        model = Competition
        fields = ['problem', 'id', 'start_time', 'end_time']

class CompetitionProblemCheckSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    public = serializers.BooleanField()
    data_description = serializers.CharField()
    data = serializers.FileField()
    solution = serializers.FileField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()