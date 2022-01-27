from rest_framework import serializers
from faq.models import Faq

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"
        #fields = ["id", "question", "answer", "created_user", "visible"]

class FaqGetAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = Faq
        #fields = ["title", "context", "created_user"]
        fields = ["id", "question", "created_time", "last_modified", "visible"]
        #fields = "__all__"

        #fields = ["title","context"]
