from rest_framework import serializers
from .models import Competition, CompetitionUser
from problem.models import Problem
from problem.serializers import ProblemSerializer, AllProblemSerializer

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'problem_id', 'start_time', 'end_time']

class CompetitionDetailSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()

    class Meta:
        model = Competition
        fields = ['problem', 'id', 'start_time', 'end_time']

class CompetitionPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['start_time', 'end_time']

class CompetitionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['problem_id', 'start_time', 'end_time']

class CompetitionListSerializer(serializers.ModelSerializer):
    problem = AllProblemSerializer()
    class Meta:
        model = Competition
        fields = ['problem', 'id', 'start_time', 'end_time']

class CompetitionProblemCheckSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    data_description = serializers.CharField()
    data = serializers.FileField()
    solution = serializers.FileField()
    evaluation = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

class CompetitionUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompetitionUser
        # fields = "__all__"
        fields = ["id", "competition_id", "username", "is_show", "privilege"]

class CompetitionUserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionUser
        fields = ["username", "privilege"]

class CompetitionUserGetInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompetitionUser
        fields = ["competition_id", "privilege"]
