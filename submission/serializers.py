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

class PathCompetitionSerializer(serializers.ModelSerializer):


    class Meta:
        model = Path
        fields = ["username", "competition_id",]