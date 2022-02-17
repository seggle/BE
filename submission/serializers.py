from rest_framework import serializers
from .models import SubmissionClass, Path


class SubmissionClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionClass
        fields = "__all__"

class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = "__all__"
