from rest_framework import serializers
from submission.models import SubmissionClass, SubmissionCompetition


class LeaderboardClassSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    score = serializers.FloatField()
    created_time = serializers.DateTimeField()
    csv = serializers.CharField()
    ipynb = serializers.CharField()

    class Meta:
        model = SubmissionClass
        fields = ["id", "username", "name", "score", "created_time", "csv", "ipynb"]

class LeaderboardCompetitionSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    score = serializers.FloatField()
    created_time = serializers.DateTimeField()
    csv = serializers.CharField()
    ipynb = serializers.CharField()

    class Meta:
        model = SubmissionCompetition
        fields = ["id", "username", "name", "score", "created_time", "csv", "ipynb"]