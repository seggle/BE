from rest_framework import serializers
from faq.models import Faq

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"
        #fields = ["id", "question", "answer", "created_user", "visible"]