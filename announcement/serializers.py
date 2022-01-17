from rest_framework import serializers
from announcement.models import Announcement


class AnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    context = serializers.CharField()
    created_user = serializers.CharField()
    created_time = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
    visible = serializers.BooleanField()
    important = serializers.BooleanField()

    def create(self, validated_data):
        print(validated_data)
        return Announcement.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.context = validated_data.get('context', instance.context)
        instance.visible = validated_data.get('visible', instance.visible)
        instance.important = validated_data.get('important', instance.important)
        instance.save()
        return instance