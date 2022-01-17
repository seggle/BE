from rest_framework import serializers
from faq.models import Faq


class FaqSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    question = serializers.CharField()
    answer = serializers.CharField()
    created_user = serializers.CharField()
    created_time = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
    visible = serializers.BooleanField()

    def create(self, validated_data):
        print(validated_data)
        return Faq.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.question = validated_data.get('title', instance.question)
        instance.answer = validated_data.get('context', instance.answer)
        instance.visible = validated_data.get('visible', instance.visible)
        instance.save()
        return instance
