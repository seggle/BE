from rest_framework import serializers
from .models import Exam


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class ExamGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        exclude = ["start_time", "exception"]
