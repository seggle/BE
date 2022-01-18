from rest_framework import serializers
from announcement.models import Announcement


class AnnouncementSerializer (serializers.ModelSerializer):
    # created_user =

    class Meta:
        model = Announcement
        fields = "__all__"

class CreateAnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=64)
    content = serializers.CharField(max_length=1024 * 1024 * 8)
    visible = serializers.BooleanField()
    important = serializers.BooleanField()

class EditAnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=64)
    context = serializers.CharField(max_length=1024 * 1024 * 8)
    visible = serializers.BooleanField()
    important = serializers.BooleanField()
