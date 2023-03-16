from rest_framework import serializers
from .models import SubmissionClass, Path, SubmissionCompetition


class SubmissionClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionClass
        # fields = "__all__"
        fields = ["id", "username", "path", "class_id", "contest_id", "c_p_id", "problem_id", "score", "csv", "ipynb",
                  "created_time", "ip_address", "status", "on_leaderboard"]


class SubmissionCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionCompetition
        # fields = "__all__"
        fields = ["id", "username", "path", "competition_id", 'comp_p_id', "problem_id", "score", "csv", "ipynb",
                  "created_time", "ip_address", "status", "on_leaderboard"]


class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = "__all__"


class SubmissionClassListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubmissionClass
        fields = ["id", "username", "score", "created_time", "status", "on_leaderboard"]


class SubmissionCompetitionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubmissionCompetition
        fields = ["id", "username", "score", "created_time", "status", "on_leaderboard"]
