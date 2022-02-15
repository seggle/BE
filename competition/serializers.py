from rest_framework import serializers
from .models import Competition, Competition_user
from problem.models import Problem
from problem.serializers import ProblemSerializer, AllProblemSerializer

class CompetitionGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['problem_id', 'id', 'start_time', 'end_time']

class CompetitionDetailSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()

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
    problem = AllProblemSerializer()
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
    evaluation = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

class CompetitionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition_user
        fields = "__all__"

class CompetitionUserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition_user
        fields = ["username", "privilege"]

class CompetitionUserGetInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition_user
        fields = ["competition_id", "privilege"]