from rest_framework import serializers
from faq.models import Faq

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["id", "question", "answer", "created_user", "created_time", "last_modified", "visible"]

class FaqAllGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["id", "question", "created_time", "last_modified", "visible"]

class FaqPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["answer", "question", "visible"]