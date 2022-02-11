from rest_framework import serializers
from .models import Competition, Competition_user
from problem.models import Problem
from problem.serializers import ProblemSerializer, ProblemListSerializer

class CompetitionGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['problem_id', 'id', 'start_time', 'end_time']


class CompetitionDetailSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)
    class Meta:
        model = Competition
        fields = ['problem', 'id', 'start_time', 'end_time']

class CompetitionPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['start_time', 'end_time']

class CompetitionListSerializer(serializers.ModelSerializer):
    # problem = serializers.PrimaryKeyRelatedField(queryset=Problem.objects.all())
    # problem = serializers.ModelSerializer.serializers.PrimaryKeyRelatedField(queryset=Problem.objects.all())
    problem = ProblemListSerializer()
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

class CompetitionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition_user
        fields = "__all__"