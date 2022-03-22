from rest_framework import serializers
from faq.models import Faq

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        # fields = "__all__"
        fields = ["id", "question", "answer", "created_user", "created_time", "last_modified", "visible"]

class FaqAllGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        #fields = "__all__"
        fields = ["id", "question", "created_time", "last_modified", "visible"]