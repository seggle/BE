from rest_framework import serializers
from .models import SubmissionClass, Path, SubmissionCompetition


class SubmissionClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionClass
        fields = "__all__"

class SubmissionCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionCompetition
        fields = "__all__"

class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = "__all__"

class SumissionClassListSerializer(serializers.ModelSerializer):
    score = serializers.FloatField()
    created_time = serializers.DateTimeField()
    status = serializers.IntegerField()
    on_leaderboard = serializers.BooleanField()
    csv = serializers.CharField()
    ipynb = serializers.CharField()

    class Meta:
        model = SubmissionClass
        fields = ["id", "username", "score", "csv", "ipynb", "created_time", "status", "on_leaderboard"]

class SumissionCompetitionListSerializer(serializers.ModelSerializer):
    score = serializers.FloatField()
    created_time = serializers.DateTimeField()
    status = serializers.IntegerField()
    on_leaderboard = serializers.BooleanField()
    csv = serializers.CharField()
    ipynb = serializers.CharField()

    class Meta:
        model = SubmissionCompetition
        fields = ["id", "username", "score", "csv", "ipynb", "created_time", "status", "on_leaderboard"]