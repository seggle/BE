from rest_framework import serializers
from .models import Exam


# class ExamSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Exam
#         # fields = "__all__"
#         fields = ["id", "ip_address", "user", "contest", "exception", "start_time", "is_duplicated"]

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        # fields = "__all__"
        fields = ["id", "ip_address", "user", "class_id", "contest", "exception", "state", "start_time"]

# class ExamGenerateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Exam
#         exclude = ["start_time", "exception","is_duplicated"]

# class ExamIDGenerateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Exam
#         exclude = ["start_time", "exception"]